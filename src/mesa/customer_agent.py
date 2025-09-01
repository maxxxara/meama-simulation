from mesa.experimental.cell_space import CellAgent
from ..models import Customer
from typing import List
from ..models import Order
from ..tools.tools import decide_order_placement, generate_campaign_impact_factor
from datetime import datetime
from ..tools.generate_custom_order import generate_customer_order
from config import BASE_CAMPAIGN_IMPACT_FACTOR

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

        self.campaign_impact_factor = BASE_CAMPAIGN_IMPACT_FACTOR
        self.hasWonImpactFactor : float = 1.0
        self.prize_wins = []
        self.new_order_count = 0
        self.campaign_spending = 0.0  # Track spending during campaign period


    def step(self):
        if hasattr(self.model, 'current_date'):  # Check if it's a CustomerModel by checking for its unique attribute
            current_date = self.model.current_date # type: ignore
            
            # Handle case where customer has no historical orders
            if not self.historical_orders:
                days_since_first_order = 365  # Use 1 year as baseline for new customers
            else:
                first_order_date = datetime.fromisoformat(self.historical_orders[0].order_date).replace(tzinfo=None)
                days_since_first_order = max((current_date - first_order_date).days, 30)  # Minimum 30 days

            # Disable campaign
            # self.campaign_impact_factor = generate_campaign_impact_factor(self.campaign_impact_factor, self.new_order_count, current_date)
            will_order = decide_order_placement(
                campaign_impact_factor=self.campaign_impact_factor,
                historical_orders=self.historical_orders,
                historical_days=days_since_first_order, 
                current_date=current_date
            )

            if will_order:
                self.tickets_count += 1
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
                        tickets_count=self.tickets_count
                    ),
                    current_date=current_date
                )
                self.model.generated_revenue += new_order.total_spent # type: ignore
                self.historical_orders.append(new_order)
                self.historical_spending += new_order.total_spent
                self.total_orders += 1
                self.avg_order_value = self.historical_spending / self.total_orders
                self.new_order_count += 1
                self.campaign_spending += new_order.total_spent
                self.model.received_orders_count += 1 # type: ignore


