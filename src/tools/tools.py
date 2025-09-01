import random
from datetime import datetime
from typing import List
from config import *

from ..models import Customer, CampaignEngagementMetrics, Order, CustomerLifecycleState
def _parse_date(date_input):
    if isinstance(date_input, str):
        if 'T' in date_input:
            dt = datetime.fromisoformat(date_input.replace('Z', '+00:00'))
            return dt.replace(tzinfo=None)
        else:
            return datetime.strptime(date_input, "%Y-%m-%d")
    elif hasattr(date_input, 'tzinfo') and date_input.tzinfo is not None:
        return date_input.replace(tzinfo=None)
    return date_input

def decide_order_placement(campaign_impact_factor: float, historical_orders: List[Order], historical_days: int, current_date: datetime, customer_data=None) -> bool:
    """
    Predicts whether a user will place an order on a specific day using comprehensive realistic purchase behavior modeling.
    
    Arguments:
    campaign_impact_factor (float): Campaign impact factor (ignored if ENABLE_CAMPAIGN_EFFECTS=False)
    historical_orders (Orders array): The array of orders placed by the user in the past.
    historical_days (int): The number of days in which the orders were placed. Current date - Customer's first order date.
    current_date (str or datetime): Current simulation date (format: "2025-10-15" or datetime object)
    customer_data (Customer, optional): Full customer data for enhanced modeling

    Returns:
    bool: True, if the user will place an order, False - if not.
    """
    import math
    from config import (ENABLE_CAMPAIGN_EFFECTS, NEW_CUSTOMER_BASELINE_PROBABILITY, 
                       WEEKEND_IMPULSE_BOOST, PAYDAY_BOOST_DAYS, SATISFACTION_LOW_THRESHOLD,
                       SATISFACTION_HIGH_THRESHOLD, IMPULSE_PURCHASE_THRESHOLD, 
                       PLANNED_PURCHASE_THRESHOLD, SEASONAL_BOOST_MONTHS, SEASONAL_BOOST_FACTOR,
                       SEASONAL_LOW_MONTHS, SEASONAL_LOW_FACTOR, ECONOMIC_SENTIMENT_FACTOR,
                       PRODUCT_DISCOVERY_BOOST, PRODUCT_INTEREST_DECLINE_RATE,
                       HIGH_PRICE_SENSITIVITY_THRESHOLD, LOW_PRICE_SENSITIVITY_THRESHOLD,
                       PRICE_SENSITIVE_REDUCTION_FACTOR, HIGH_BRAND_LOYALTY_THRESHOLD,
                       LOW_BRAND_LOYALTY_THRESHOLD, BRAND_LOYALTY_BOOST_FACTOR,
                       SATISFACTION_DECAY_RATE, SATISFACTION_RECOVERY_RATE,
                       PURCHASE_INTENT_DECAY_RATE, PURCHASE_INTENT_BOOST_AFTER_BROWSE)

    historical_orders_count = len(historical_orders)
    current = _parse_date(current_date)

    # --- Step 1: Calculate base purchase probability ---
    if historical_days <= 0 or historical_orders_count == 0:
        # New customers: much lower baseline probability
        base_daily_probability = NEW_CUSTOMER_BASELINE_PROBABILITY * 0.1
    else:
        # Calculate realistic purchase frequency based on history
        avg_days_between_purchases = max(historical_days / max(historical_orders_count, 1), 7)
        base_daily_probability = min(1.0 / avg_days_between_purchases, 0.02)

    # --- Step 2: Apply purchase timing factors ---
    
    # A. Recent purchase cooldown
    days_since_last_purchase = 999
    if historical_orders and len(historical_orders) > 0:
        last_order_date = _parse_date(historical_orders[-1].order_date)
        days_since_last_purchase = (current - last_order_date).days
    
    if days_since_last_purchase < 3:
        cooldown_factor = 0.05
    elif days_since_last_purchase < 7:
        cooldown_factor = 0.2
    elif days_since_last_purchase < 14:
        cooldown_factor = 0.5
    elif days_since_last_purchase < 30:
        cooldown_factor = 0.8
    else:
        cooldown_factor = 1.0

    # B. Day of week factor
    day_of_week = current.weekday()
    if day_of_week == 4:  # Friday
        day_factor = 1.2
    elif day_of_week in [5, 6]:  # Weekend
        day_factor = 1.1 * WEEKEND_IMPULSE_BOOST
    elif day_of_week == 0:  # Monday
        day_factor = 0.9
    else:
        day_factor = 1.0

    # C. Monthly budget cycle factor with payday boosts
    day_of_month = current.day
    payday_boost = 1.0
    if day_of_month in PAYDAY_BOOST_DAYS:
        payday_boost = 1.2
    
    if day_of_month <= 5:
        budget_cycle_factor = 1.3 * payday_boost
    elif day_of_month <= 15:
        budget_cycle_factor = 1.0 * payday_boost
    elif day_of_month <= 25:
        budget_cycle_factor = 0.8
    else:
        budget_cycle_factor = 0.7

    # --- Step 3: Enhanced customer behavior factors ---
    
    # Initialize default values if customer_data not provided
    satisfaction_factor = 1.0
    purchase_intent_factor = 1.0
    seasonal_factor = 1.0
    price_sensitivity_factor = 1.0
    brand_loyalty_factor = 1.0
    product_interest_factor = 1.0
    
    if customer_data:
        # D. Customer satisfaction impact
        satisfaction = customer_data.satisfaction_score
        if satisfaction < SATISFACTION_LOW_THRESHOLD:
            satisfaction_factor = 0.2  # 80% reduction for dissatisfied customers
        elif satisfaction > SATISFACTION_HIGH_THRESHOLD:
            satisfaction_factor = 1.3  # 30% boost for highly satisfied customers
        else:
            satisfaction_factor = 0.5 + satisfaction  # Linear scaling between 0.5-1.0

        # E. Purchase intent modeling
        intent = customer_data.purchase_intent_level
        if intent < IMPULSE_PURCHASE_THRESHOLD:
            # Low intent - only impulse purchases possible
            purchase_intent_factor = 0.3 * (1.0 if day_of_week in [5, 6] else 0.5)
        elif intent > PLANNED_PURCHASE_THRESHOLD:
            # High intent - planned purchase behavior
            purchase_intent_factor = 1.5
        else:
            # Medium intent - normal behavior
            purchase_intent_factor = 0.7 + (intent * 0.6)

        # F. Price sensitivity impact
        if customer_data.price_sensitivity > HIGH_PRICE_SENSITIVITY_THRESHOLD:
            price_sensitivity_factor = PRICE_SENSITIVE_REDUCTION_FACTOR
        elif customer_data.price_sensitivity < LOW_PRICE_SENSITIVITY_THRESHOLD:
            price_sensitivity_factor = 1.1  # Slight boost for price insensitive

        # G. Brand loyalty impact
        if customer_data.brand_loyalty > HIGH_BRAND_LOYALTY_THRESHOLD:
            brand_loyalty_factor = BRAND_LOYALTY_BOOST_FACTOR
        elif customer_data.brand_loyalty < LOW_BRAND_LOYALTY_THRESHOLD:
            brand_loyalty_factor = 0.7  # Reduction for low loyalty

        # H. Recent negative experience impact
        if customer_data.last_negative_experience_days < 14:
            satisfaction_factor *= 0.3  # Strong negative impact for 2 weeks

    # I. Seasonal factors
    current_month = current.month
    if current_month in SEASONAL_BOOST_MONTHS:
        seasonal_factor = SEASONAL_BOOST_FACTOR
    elif current_month in SEASONAL_LOW_MONTHS:
        seasonal_factor = SEASONAL_LOW_FACTOR

    # J. Economic sentiment factor
    economic_factor = ECONOMIC_SENTIMENT_FACTOR

    # K. Product interest fluctuation (simulated)
    # Simulate occasional "product discovery" that boosts interest
    if random.random() < 0.1:  # 10% chance of product discovery
        product_interest_factor = 1.0 + PRODUCT_DISCOVERY_BOOST
    else:
        # Gradual decline in interest over time
        days_factor = min(days_since_last_purchase * PRODUCT_INTEREST_DECLINE_RATE, 0.3)
        product_interest_factor = 1.0 - days_factor

    # --- Step 4: Calculate comprehensive adjusted probability ---
    comprehensive_probability = (
        base_daily_probability *
        cooldown_factor *
        day_factor *
        budget_cycle_factor *
        satisfaction_factor *
        purchase_intent_factor *
        seasonal_factor *
        price_sensitivity_factor *
        brand_loyalty_factor *
        product_interest_factor *
        economic_factor
    )

    # --- Step 5: Apply campaign effects if enabled ---
    if ENABLE_CAMPAIGN_EFFECTS:
        # Check if we're in campaign period
        current_month = current.month
        if current >= _parse_date(CAMPAIGN_START) and current <= _parse_date(CAMPAIGN_END):
            # We're in campaign period - apply strong effects
            if campaign_impact_factor > 1.0:
                # Much more aggressive campaign multiplier for noticeable impact
                campaign_multiplier = campaign_impact_factor * 0.8  # Reduce dampening significantly
            else:
                campaign_multiplier = campaign_impact_factor
            
            # Additional campaign-specific boosts
            campaign_urgency_boost = 1.0
            days_left = (_parse_date(CAMPAIGN_END) - current).days
            if days_left <= 7:  # Last week urgency
                campaign_urgency_boost = 1.4
            elif days_left <= 30:  # Last month urgency
                campaign_urgency_boost = 1.2
            
            # Customer reactivation boost - dormant customers get extra motivation during campaigns
            reactivation_boost = 1.0
            if customer_data and customer_data.lifecycle_state == CustomerLifecycleState.DORMANT:
                reactivation_boost = 1.8  # 80% boost for dormant customers
            elif customer_data and customer_data.lifecycle_state == CustomerLifecycleState.AT_RISK:
                reactivation_boost = 1.4  # 40% boost for at-risk customers
            
            # Special promotional days (simulate flash sales, special offers)
            promotional_boost = 1.0
            if current.day in [1, 15]:  # Twice a month "flash sales"
                promotional_boost = 1.3
            
            final_probability = (comprehensive_probability * 
                               campaign_multiplier * 
                               campaign_urgency_boost * 
                               reactivation_boost * 
                               promotional_boost)
            
            # Higher cap during campaigns for significant impact
            final_probability = min(final_probability, 0.08)  # 8% max during campaigns vs 2% baseline
        else:
            # Outside campaign period
            final_probability = comprehensive_probability
    else:
        final_probability = comprehensive_probability
    
    # Apply different caps based on campaign status
    if ENABLE_CAMPAIGN_EFFECTS and current >= _parse_date(CAMPAIGN_START) and current <= _parse_date(CAMPAIGN_END):
        # During campaigns, allow higher probability for impact
        final_probability = min(final_probability, 0.08)  # 8% max during campaigns
    else:
        # Outside campaigns, conservative cap
        final_probability = min(final_probability, 0.02)  # 2% max normally
    
    # --- Step 6: Final decision with reality checks ---
    random_number = random.random()
    
    # Ultimate safeguard against unrealistic purchasing
    if days_since_last_purchase < 2 and random.random() > 0.95:
        return False
    
    # Customer satisfaction-based rejection
    if customer_data and customer_data.satisfaction_score < 0.2 and random.random() > 0.1:
        return False
    
    return random_number <= final_probability


def generate_campaign_impact_factor(current_customer_impact_factor: float, campaign_orders_count: int, current_date) -> float:
    """
    Generates a dynamic campaign impact factor based on customer's order activity during the campaign period.
    
    The impact factor starts with a base value and increases based on how many orders the customer
    has placed during the ongoing campaign period. Uses logarithmic scaling to prevent unrealistic growth.
    Returns 1.0 (no effect) if ENABLE_CAMPAIGN_EFFECTS is False.
    
    Arguments:
    current_customer_impact_factor (float): Current impact factor for the customer
    campaign_orders_count (int): Number of orders placed during current campaign
    current_date (str or datetime): Current simulation date (format: "2025-10-15" or datetime object)
    
    Returns:
    float: Campaign impact factor (e.g., 1.3 = 30% increase, 1.5 = 50% increase, 1.0 = no campaign)
    """
    import math
    from config import ENABLE_CAMPAIGN_EFFECTS

    # If campaign effects are disabled, always return baseline (no campaign effect)
    if not ENABLE_CAMPAIGN_EFFECTS:
        return 1.0

    campaign_start = CAMPAIGN_START
    campaign_end = CAMPAIGN_END
    current = _parse_date(current_date)
    
    # If we're not in the campaign period, return 1.0 (no campaign effect)
    if current < campaign_start or current > campaign_end:
        return 1.0
    
    # More linear scaling for noticeable engagement boost
    if campaign_orders_count > 0:
        # Use square root scaling for moderate diminishing returns but stronger initial impact
        engagement_boost = math.sqrt(campaign_orders_count) * CAMPAIGN_ENGAGEMENT_MULTIPLIER
    else:
        engagement_boost = 0
    
    # Calculate dynamic impact factor with logarithmic scaling
    dynamic_factor = current_customer_impact_factor + engagement_boost
    
    # Apply campaign fatigue after many orders (reduces effectiveness)
    if campaign_orders_count > 8:  # After 8 orders, apply fatigue
        fatigue_factor = 1.0 - (campaign_orders_count - 8) * 0.02  # 2% reduction per order after 8th
        dynamic_factor *= max(fatigue_factor, 0.8)  # Minimum 80% effectiveness
    
    # Cap the maximum impact factor to prevent unrealistic probabilities
    dynamic_factor = min(dynamic_factor, MAX_CAMPAIGN_IMPACT_FACTOR)
    dynamic_factor = max(dynamic_factor, 1.0)  # Ensure it's never below baseline
    
    return dynamic_factor


def decide_new_customer_acquisition(current_date, existing_customers_count, campaign_engagement_metrics: CampaignEngagementMetrics | None = None) -> List[Customer]:
    """
    Determines how many new customers should be acquired on a specific day.
    
    When ENABLE_CAMPAIGN_EFFECTS is True:
    - Enhanced acquisition during campaign periods with timing, engagement, and word-of-mouth effects
    - Higher rates during peak campaign periods, lower baseline rates outside campaigns
    
    When ENABLE_CAMPAIGN_EFFECTS is False:
    - Steady vanilla acquisition rate throughout the simulation period
    - No campaign-specific timing or engagement boosts
    
    Arguments:
    current_date (str or datetime): Current simulation date (format: "2025-10-15" or datetime object)
    existing_customers_count (int): Total number of existing customers in the system
    campaign_engagement_metrics (dict, optional): Metrics about campaign performance (ignored if campaigns disabled)
    
    Returns:
    List[Customer]: List of new customer data structures
    """
    
    from config import ENABLE_CAMPAIGN_EFFECTS
    
    current = _parse_date(current_date)
    
    # If campaign effects are disabled, use vanilla acquisition throughout
    if not ENABLE_CAMPAIGN_EFFECTS:
        # Vanilla acquisition: much more realistic rate
        vanilla_acquisition_rate = 0.001  # 0.1% daily probability (realistic for business growth)
        should_acquire = random.random() <= vanilla_acquisition_rate
        if should_acquire:
            new_customer = Customer(
                id=existing_customers_count + 1,
                email=f"newcustomer{existing_customers_count + 1}@example.com",
                created_at=current,
                historical_purchase_frequency=[],
                historical_spending=0,
                average_order_value=0,
                total_orders=0,
                is_new_customer=True,
                tickets_count=0,  # Start with 0 tickets, no immediate order
                lifecycle_state=CustomerLifecycleState.ACTIVE
            )
            # Don't create an immediate order - let new customers decide naturally
            return [new_customer]
        return []
    
    # Campaign effects enabled - use enhanced acquisition logic
    # If we're not in the campaign period, use baseline acquisition rate
    if current < CAMPAIGN_START or current > CAMPAIGN_END:
        should_acquire = random.random() <= CUSTOMER_ACQUISITION_AFTER_CAMPAIGN_END
        if should_acquire:
            new_customer = Customer(
                id=existing_customers_count + 1,
                email=f"newcustomer{existing_customers_count + 1}@example.com",
                created_at=current,
                historical_purchase_frequency=[],
                historical_spending=0,
                average_order_value=0,
                total_orders=0,
                is_new_customer=True,
                tickets_count=0,  # Start with 0 tickets, no immediate order
                lifecycle_state=CustomerLifecycleState.ACTIVE
            )
            # Don't create an immediate order - let new customers decide naturally
            return [new_customer]
        return [] 
    
    # Calculate campaign progress (0.0 to 1.0)
    campaign_duration = (CAMPAIGN_END - CAMPAIGN_START).days
    days_into_campaign = (current - CAMPAIGN_START).days
    campaign_progress = min(days_into_campaign / campaign_duration, 1.0)
    
    # Base acquisition rate during campaign
    base_campaign_rate = CUSTOMER_ACQUISITION_CAMPAIGN_BIAS 
    
    # Campaign timing factor - higher rates at the beginning and end
    if campaign_progress < CUSTOMER_ACQUISITION_EARLY_CAMPAIGN_THRESHOLD:
        # Early campaign excitement
        timing_factor = CUSTOMER_ACQUISITION_EARLY_CAMPAIGN_BOOST
    elif campaign_progress > CUSTOMER_ACQUISITION_LATE_CAMPAIGN_THRESHOLD:
        # End-of-campaign urgency
        timing_factor = CUSTOMER_ACQUISITION_LATE_CAMPAIGN_BOOST
    else:
        # Mid-campaign steady state
        timing_factor = 1.0
    
    # Word-of-mouth effect based on campaign engagement
    word_of_mouth_factor = 1.0
    if campaign_engagement_metrics:
        total_orders = campaign_engagement_metrics.total_orders
        active_customers = campaign_engagement_metrics.active_customers
        
        # More orders and active customers = better word-of-mouth
        if total_orders > 0 and active_customers > 0:
            engagement_score = min(total_orders / active_customers, CUSTOMER_ACQUISITION_WORD_OF_MOUTH_MAX_ENGAGEMENT)
            word_of_mouth_factor = 1.0 + (engagement_score * CUSTOMER_ACQUISITION_WORD_OF_MOUTH_MULTIPLIER)
    
    # Market saturation factor - diminishing returns as customer base grows
    saturation_factor = max(CUSTOMER_ACQUISITION_SATURATION_MIN_FACTOR, 1.0 - (existing_customers_count / (existing_customers_count / 2)))
    
    # Day of week factor - weekends typically have higher acquisition rates
    day_of_week = current.weekday()
    if day_of_week >= 5:  # Weekend (Saturday=5, Sunday=6)
        day_factor = CUSTOMER_ACQUISITION_WEEKEND_BOOST
    else:
        day_factor = 1.0
    
    # Calculate final acquisition probability
    acquisition_probability = (
        base_campaign_rate * 
        timing_factor * 
        word_of_mouth_factor * 
        saturation_factor * 
        day_factor
    )
    
    # Cap the probability to reasonable limits
    acquisition_probability = min(acquisition_probability, PROPORTION_OF_NEW_CUSTOMERS)  # Max 25% daily rate
    
    # Determine number of customers to acquire using a more aggressive approach
    # Use Poisson distribution for more realistic customer acquisition modeling
    import math
    
    # Calculate expected number of customers to acquire
    expected_customers = acquisition_probability * MAX_CUSTOMERS_PER_DAY
    
    # Use Poisson distribution to determine actual number of customers
    # This provides more realistic variation while maintaining the expected rate
    customers_to_acquire = 0
    for _ in range(MAX_CUSTOMERS_PER_DAY):
        if random.random() <= acquisition_probability:
            customers_to_acquire += 1
    
    # Add some bonus customers on high-engagement days (weekends, campaign peaks)
    if day_factor > 1.0 and random.random() < 0.3:  # 30% chance of bonus customers on weekends
        customers_to_acquire += random.randint(1, 3)
    
    # Ensure we don't exceed the maximum
    customers_to_acquire = min(customers_to_acquire, MAX_CUSTOMERS_PER_DAY)
    
    # Generate customer data and orders for all acquired customers
    new_customers_data : List[Customer] = []
    
    for i in range(customers_to_acquire):
        new_customer_data = Customer(
            id=existing_customers_count + i + 1,
            email=f"newcustomer{existing_customers_count + i + 1}@example.com",
            created_at=current,
            historical_purchase_frequency=[],
            historical_spending=0,
            average_order_value=0,
            total_orders=0,
            is_new_customer=True,
            tickets_count=1,
            lifecycle_state=CustomerLifecycleState.ACTIVE
        )
        from .generate_custom_order import generate_customer_order
        new_order = generate_customer_order(new_customer_data, current_date)
        new_customer_data.historical_purchase_frequency.append(new_order)
        new_customers_data.append(new_customer_data)
    
    return new_customers_data


def update_customer_satisfaction(customer_data, days_passed: int, had_purchase: bool = False, had_negative_experience: bool = False):
    """
    Updates customer satisfaction based on time and experiences.
    
    Arguments:
    customer_data: Customer object to update
    days_passed: Number of days since last update
    had_purchase: Whether customer made a purchase (positive experience)
    had_negative_experience: Whether customer had a negative experience
    """
    if not hasattr(customer_data, 'satisfaction_score'):
        customer_data.satisfaction_score = 0.7  # Default satisfaction
    
    # Natural satisfaction decay over time
    decay = days_passed * SATISFACTION_DECAY_RATE
    customer_data.satisfaction_score = max(0.0, customer_data.satisfaction_score - decay)
    
    # Recovery from negative experiences
    if customer_data.last_negative_experience_days < 999:
        customer_data.last_negative_experience_days += days_passed
        if customer_data.last_negative_experience_days > 30:  # After 30 days, start recovery
            recovery = (customer_data.last_negative_experience_days - 30) * SATISFACTION_RECOVERY_RATE
            customer_data.satisfaction_score = min(1.0, customer_data.satisfaction_score + recovery)
    
    # Positive experience boost
    if had_purchase:
        customer_data.satisfaction_score = min(1.0, customer_data.satisfaction_score + 0.1)
    
    # Negative experience impact
    if had_negative_experience:
        customer_data.satisfaction_score = max(0.0, customer_data.satisfaction_score - 0.3)
        customer_data.last_negative_experience_days = 0


def update_purchase_intent(customer_data, days_passed: int, simulated_browsing: bool = False):
    """
    Updates customer purchase intent based on time and browsing behavior.
    
    Arguments:
    customer_data: Customer object to update
    days_passed: Number of days since last update
    simulated_browsing: Whether customer "browsed" products (random simulation)
    """
    if not hasattr(customer_data, 'purchase_intent_level'):
        customer_data.purchase_intent_level = 0.5
    
    # Natural intent decay
    decay = days_passed * PURCHASE_INTENT_DECAY_RATE
    customer_data.purchase_intent_level = max(0.0, customer_data.purchase_intent_level - decay)
    
    # Browsing behavior boost (simulated)
    if simulated_browsing or random.random() < 0.15:  # 15% daily chance of "browsing"
        customer_data.purchase_intent_level = min(1.0, customer_data.purchase_intent_level + PURCHASE_INTENT_BOOST_AFTER_BROWSE)


def update_customer_lifecycle_state(customer_data, current_date: datetime):
    """
    Updates customer lifecycle state based on purchase behavior and patterns.
    
    Arguments:
    customer_data: Customer object to update
    current_date: Current simulation date
    """
    from datetime import timedelta
    
    if not customer_data.historical_purchase_frequency:
        customer_data.lifecycle_state = CustomerLifecycleState.ACTIVE
        return
    
    # Calculate days since last order
    last_order = customer_data.historical_purchase_frequency[-1]
    last_order_date = _parse_date(last_order.order_date)
    days_since_last_order = (current_date - last_order_date).days
    
    # Calculate customer metrics
    total_spent = sum(order.total_spent for order in customer_data.historical_purchase_frequency)
    avg_order_value = total_spent / len(customer_data.historical_purchase_frequency) if customer_data.historical_purchase_frequency else 0
    order_frequency = len(customer_data.historical_purchase_frequency) / max((current_date - customer_data.created_at).days / 30, 1)  # Orders per month
    
    # Determine lifecycle state
    if days_since_last_order > 180:  # 6 months
        customer_data.lifecycle_state = CustomerLifecycleState.DORMANT
    elif days_since_last_order > 90 and order_frequency < 0.5:  # 3 months + low frequency
        customer_data.lifecycle_state = CustomerLifecycleState.AT_RISK
    elif avg_order_value > 50 and order_frequency > 1.0:  # High value + frequent
        customer_data.lifecycle_state = CustomerLifecycleState.CHAMPION
    else:
        customer_data.lifecycle_state = CustomerLifecycleState.ACTIVE


def simulate_random_customer_experiences(customer_data, current_date: datetime):
    """
    Simulates random positive and negative customer experiences to add realism.
    
    Arguments:
    customer_data: Customer object to update
    current_date: Current simulation date
    """
    # Random chance of negative experience (shipping delays, product issues, etc.)
    if random.random() < 0.02:  # 2% daily chance
        update_customer_satisfaction(customer_data, 0, had_negative_experience=True)
    
    # Random chance of positive experience (great customer service, product discovery, etc.)
    if random.random() < 0.05:  # 5% daily chance
        customer_data.satisfaction_score = min(1.0, customer_data.satisfaction_score + 0.05)
    
    # Random fluctuations in brand loyalty based on market factors
    if random.random() < 0.01:  # 1% daily chance
        loyalty_change = random.uniform(-0.1, 0.1)
        customer_data.brand_loyalty = max(0.0, min(1.0, customer_data.brand_loyalty + loyalty_change))
    
    # Price sensitivity can change based on economic conditions
    if random.random() < 0.005:  # 0.5% daily chance
        sensitivity_change = random.uniform(-0.05, 0.05)
        customer_data.price_sensitivity = max(0.0, min(1.0, customer_data.price_sensitivity + sensitivity_change))
