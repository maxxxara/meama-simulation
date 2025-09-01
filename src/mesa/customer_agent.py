from mesa.experimental.cell_space import CellAgent
from ..models import Customer, CustomerLifecycleState
from typing import List
from ..models import Order
from ..tools.tools import decide_order_placement, generate_campaign_impact_factor, update_customer_satisfaction, update_purchase_intent, update_customer_lifecycle_state, simulate_random_customer_experiences
from datetime import datetime, timedelta
from ..tools.generate_custom_order import generate_customer_order
from config import BASE_CAMPAIGN_IMPACT_FACTOR
import random

class CustomerAgent(CellAgent):
    """A Customer agent that represents a customer in the simulation.

    Attributes:
        customer_id: Unique customer identifier
        email: Customer email address
        historical_spending: Total historical spending
        avg_order_value: Average order value
        total_orders: Total number of orders (integer)
        historical_orders: List of historical order objects
        is_new_customer: Whether this is a new customer
    """

    def __init__(self, model, customer_data: Customer):
        """Args:
        model: The model instance.
        customer_data: The customer data object.
        """
        super().__init__(model)

        self.customer_id = customer_data.id
        self.email = customer_data.email
        self.historical_spending = customer_data.historical_spending
        self.avg_order_value = customer_data.average_order_value
        self.total_orders = customer_data.total_orders  # This should be an integer
        self.historical_orders = customer_data.historical_purchase_frequency  # This is the list of Order objects
        self.is_new_customer = customer_data.is_new_customer
        self.tickets_count = customer_data.tickets_count
        self.lifecycle_state = customer_data.lifecycle_state or CustomerLifecycleState.ACTIVE

        self.campaign_impact_factor = BASE_CAMPAIGN_IMPACT_FACTOR
        self.hasWonImpactFactor : float = 1.0
        self.prize_wins = []
        self.new_order_count = 0
        self.is_churned = False
        self.days_since_last_order = 0
        
        # Initialize enhanced customer attributes with realistic defaults
        self.satisfaction_score = getattr(customer_data, 'satisfaction_score', random.uniform(0.5, 0.9))
        self.purchase_intent_level = getattr(customer_data, 'purchase_intent_level', random.uniform(0.3, 0.7))
        self.price_sensitivity = getattr(customer_data, 'price_sensitivity', random.uniform(0.2, 0.8))
        self.brand_loyalty = getattr(customer_data, 'brand_loyalty', random.uniform(0.3, 0.8))
        self.last_negative_experience_days = getattr(customer_data, 'last_negative_experience_days', 999)


    def update_lifecycle_state(self, current_date: datetime):
        """Update customer lifecycle state based on purchase patterns."""
        if not self.historical_orders:
            self.lifecycle_state = CustomerLifecycleState.ACTIVE if self.is_new_customer else CustomerLifecycleState.DORMANT
            return
        
        # Find last order date
        last_order_date = max([datetime.fromisoformat(order.order_date.replace('Z', '+00:00')).replace(tzinfo=None) 
                              for order in self.historical_orders])
        self.days_since_last_order = (current_date - last_order_date).days
        
        # Calculate purchase frequency over last 6 months
        six_months_ago = current_date - timedelta(days=180)
        recent_orders = [order for order in self.historical_orders 
                        if datetime.fromisoformat(order.order_date.replace('Z', '+00:00')).replace(tzinfo=None) >= six_months_ago]
        
        # Lifecycle state logic
        if self.days_since_last_order > 180:  # 6+ months
            self.lifecycle_state = CustomerLifecycleState.DORMANT
        elif len(recent_orders) >= 10 and self.avg_order_value > 50:  # High frequency + high value
            self.lifecycle_state = CustomerLifecycleState.CHAMPION
        elif len(recent_orders) >= 3:  # Regular activity
            # Check if declining (compare recent vs older patterns)
            older_period = current_date - timedelta(days=360)
            older_orders = [order for order in self.historical_orders 
                           if six_months_ago > datetime.fromisoformat(order.order_date.replace('Z', '+00:00')).replace(tzinfo=None) >= older_period]
            
            if len(older_orders) > len(recent_orders) * 1.5:  # Declining trend
                self.lifecycle_state = CustomerLifecycleState.AT_RISK
            else:
                self.lifecycle_state = CustomerLifecycleState.ACTIVE
        else:
            self.lifecycle_state = CustomerLifecycleState.ACTIVE
    
    def calculate_churn_probability(self, current_date: datetime) -> float:
        """Calculate probability that customer will churn (stop purchasing)."""
        base_churn_probability = 0.001  # 0.1% base daily churn rate
        
        # Adjust based on lifecycle state
        lifecycle_multipliers = {
            CustomerLifecycleState.CHAMPION: 0.2,   # Very low churn
            CustomerLifecycleState.ACTIVE: 1.0,     # Base churn
            CustomerLifecycleState.AT_RISK: 3.0,    # Higher churn
            CustomerLifecycleState.DORMANT: 5.0     # Highest churn
        }
        
        churn_probability = base_churn_probability * lifecycle_multipliers[self.lifecycle_state]
        
        # Additional factors
        if self.days_since_last_order > 90:  # 3+ months since last order
            churn_probability *= (1 + self.days_since_last_order / 365)
        
        # Campaign fatigue (if customer has many recent orders but low engagement)
        if self.new_order_count > 5 and self.campaign_impact_factor < 1.2:
            churn_probability *= 1.5
        
        return min(churn_probability, 0.05)  # Cap at 5% daily churn

    def step(self):
        if hasattr(self.model, 'current_date'):  # Check if it's a CustomerModel by checking for its unique attribute
            current_date = self.model.current_date # type: ignore
            
            # Update lifecycle state and check for churn
            self.update_lifecycle_state(current_date)
            
            # Check for churn
            if not self.is_churned:
                churn_probability = self.calculate_churn_probability(current_date)
                if random.random() <= churn_probability:
                    self.is_churned = True
                    return  # Churned customers don't make purchases
            else:
                return  # Churned customers don't participate
            
            # Handle case where customer has no historical orders
            if not self.historical_orders:
                days_since_first_order = 365  # Use 1 year as baseline for new customers
            else:
                first_order_date = datetime.fromisoformat(self.historical_orders[0].order_date).replace(tzinfo=None)
                days_since_first_order = max((current_date - first_order_date).days, 30)  # Minimum 30 days

            # Apply lifecycle-specific purchase probability adjustments
            lifecycle_purchase_multipliers = {
                CustomerLifecycleState.CHAMPION: 1.3,   # 30% higher probability
                CustomerLifecycleState.ACTIVE: 1.0,     # Base probability
                CustomerLifecycleState.AT_RISK: 0.7,    # 30% lower probability  
                CustomerLifecycleState.DORMANT: 0.3     # 70% lower probability
            }
            
            adjusted_campaign_impact = self.campaign_impact_factor * lifecycle_purchase_multipliers[self.lifecycle_state]
            
            self.campaign_impact_factor = generate_campaign_impact_factor(adjusted_campaign_impact, self.new_order_count, current_date)
            
            # Update customer behavioral attributes daily
            customer_data_obj = Customer(
                id=self.customer_id,
                email=self.email,
                created_at=current_date,
                historical_purchase_frequency=self.historical_orders,
                historical_spending=self.historical_spending,
                average_order_value=self.avg_order_value,
                total_orders=self.total_orders,
                is_new_customer=self.is_new_customer,
                tickets_count=self.tickets_count,
                lifecycle_state=self.lifecycle_state,
                satisfaction_score=self.satisfaction_score,
                purchase_intent_level=self.purchase_intent_level,
                price_sensitivity=self.price_sensitivity,
                brand_loyalty=self.brand_loyalty,
                last_negative_experience_days=self.last_negative_experience_days
            )
            
            # Update customer attributes based on daily progression
            update_customer_satisfaction(customer_data_obj, 1)  # 1 day passed
            update_purchase_intent(customer_data_obj, 1)
            update_customer_lifecycle_state(customer_data_obj, current_date)
            simulate_random_customer_experiences(customer_data_obj, current_date)
            
            # Sync updated values back to agent
            self.satisfaction_score = customer_data_obj.satisfaction_score
            self.purchase_intent_level = customer_data_obj.purchase_intent_level
            self.price_sensitivity = customer_data_obj.price_sensitivity
            self.brand_loyalty = customer_data_obj.brand_loyalty
            self.last_negative_experience_days = customer_data_obj.last_negative_experience_days
            self.lifecycle_state = customer_data_obj.lifecycle_state
            
            will_order = decide_order_placement(
                campaign_impact_factor=self.campaign_impact_factor,
                historical_orders=self.historical_orders,
                historical_days=days_since_first_order, 
                current_date=current_date,
                customer_data=customer_data_obj
            )

            if will_order:
                self.tickets_count += 1
                self.days_since_last_order = 0  # Reset counter
                
                # Apply positive satisfaction boost from successful purchase
                update_customer_satisfaction(customer_data_obj, 0, had_purchase=True)
                self.satisfaction_score = customer_data_obj.satisfaction_score
                
                # Reset purchase intent after making a purchase
                self.purchase_intent_level = max(0.1, self.purchase_intent_level - 0.3)
                
                new_order = generate_customer_order(
                    customer_data=Customer(
                        id=self.customer_id,
                        email=self.email,
                        historical_spending=self.historical_spending,
                        average_order_value=self.avg_order_value,
                        total_orders=self.total_orders,
                        created_at=current_date.strftime("%Y-%m-%d"),
                        is_new_customer=self.is_new_customer,
                        historical_purchase_frequency=self.historical_orders,
                        tickets_count=self.tickets_count,
                        lifecycle_state=self.lifecycle_state
                    ),
                    current_date=current_date
                )
                self.model.generated_revenue += new_order.total_spent # type: ignore
                self.historical_orders.append(new_order)
                self.historical_spending += new_order.total_spent
                self.total_orders += 1
                self.avg_order_value = self.historical_spending / self.total_orders
                self.new_order_count += 1
                self.model.received_orders_count += 1 # type: ignore


