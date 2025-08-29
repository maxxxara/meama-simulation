import random
from datetime import datetime
from typing import List
from config import *

from ..models import Customer, CampaignEngagementMetrics, Order
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

def decide_order_placement(campaign_impact_factor: float, historical_orders: List[Order], historical_days: int, current_date: datetime) -> bool:
    """
    Predicts whether a user will place an order on a specific day.
    
    Arguments:
    historical_orders (Orders array): The array of orders placed by the user in the past.
    historical_days (int): The number of days in which the orders were placed. Current date - Customer's first order date.
    current_date (str or datetime): Current simulation date (format: "2025-10-15" or datetime object)

    Returns:
    bool: True, if the user will place an order, False - if not.
    """

    historical_orders_count = len(historical_orders)

    # --- Step 1: Calculating the daily order probability without the campaign ---
    # This is the customer's normal, daily activity, without the campaign.
    if historical_days <= 0 or historical_orders_count == 0:
        # For new customers or customers with no historical data,
        # use the baseline probability
        daily_probability = NEW_CUSTOMER_BASELINE_PROBABILITY
    else:
        daily_probability = historical_orders_count / historical_days
        
    # --- Step 2: Considering the campaign impact ---
    # We multiply the base probability by the campaign impact factor
    # to get the increased probability during the campaign period.
    campaign_daily_probability = daily_probability * campaign_impact_factor
    
    # Ensure the probability does not exceed 1.0 (probability cannot be greater than 100%).
    campaign_daily_probability = min(campaign_daily_probability, 1.0)
    
    
    # --- Step 3: Random decision making ---
    # We generate a random number between 0 and 1.
    # This number represents the "flip" or "randomness" for this specific day.
    random_number = random.random()
    
    # Check if the random number is less than or equal to the calculated probability.
    if random_number <= campaign_daily_probability:
        # Customer will place an order
        return True
    else:
        return False


def generate_campaign_impact_factor(current_customer_impact_factor: float, campaign_orders_count: int, current_date) -> float:
    """
    Generates a dynamic campaign impact factor based on customer's order activity during the campaign period.
    
    The impact factor starts with a base value and increases based on how many orders the customer
    has placed during the ongoing campaign period. This reflects the behavioral pattern where
    engaged customers (those who order frequently during a campaign) are more likely to continue ordering.
    
    Arguments:
    customer_orders (list): List of customer's historical orders with 'order_date' field
    current_date (str or datetime): Current simulation date (format: "2025-10-15" or datetime object)
    
    Returns:
    float: Campaign impact factor (e.g., 1.3 = 30% increase, 1.8 = 80% increase)
    
    Example:
    - Customer with 0 orders during campaign: 1.3 (base 30% increase)
    - Customer with 3 orders during campaign: 1.6 (30% + 3*10% = 60% increase)
    - Customer with 5 orders during campaign: 1.8 (30% + 5*10% = 80% increase)
    """
    

    campaign_start = CAMPAIGN_START
    campaign_end = CAMPAIGN_END
    current = _parse_date(current_date)
    
    # If we're not in the campaign period, return 1.0 (no campaign effect)
    if current < campaign_start or current > campaign_end:
        return 1.0
    
    # Calculate dynamic impact factor
    # Base factor + additional boost based on engagement level
    dynamic_factor = current_customer_impact_factor + (campaign_orders_count * CAMPAIGN_ENGAGEMENT_MULTIPLIER)
    
    # Optional: Cap the maximum impact factor to prevent unrealistic probabilities
    dynamic_factor = min(dynamic_factor, MAX_CAMPAIGN_IMPACT_FACTOR)
    
    return dynamic_factor


def decide_new_customer_acquisition(current_date, existing_customers_count, campaign_engagement_metrics: CampaignEngagementMetrics | None = None) -> List[Customer]:
    """
    Determines how many new customers should be acquired on a specific day during the campaign.
    
    This function models the rate at which new customers enter the system during the campaign period.
    The acquisition rate is influenced by:
    - Campaign timing (higher rates during peak campaign periods)
    - Existing customer base size (diminishing returns)
    - Campaign engagement metrics (word-of-mouth effect)
    - Day of week and seasonal factors
    
    Arguments:
    current_date (str or datetime): Current simulation date (format: "2025-10-15" or datetime object)
    existing_customers_count (int): Total number of existing customers in the system
    campaign_engagement_metrics (dict, optional): Metrics about campaign performance including:
        - total_orders: Total orders placed during campaign
        - active_customers: Number of customers who placed orders during campaign
        - average_order_value: Average order value during campaign
    max_customers_per_day (int): Maximum number of customers that can be acquired in one day (default: 5)
    
    Returns:
    dict: Dictionary containing:
        - 'customers_to_acquire': int - Number of customers to acquire (0 to max_customers_per_day)
        - 'new_customers_data': list - List of new customer data structures
    
    Example:
    - Early campaign: Higher acquisition rates due to initial excitement
    - Mid campaign: Moderate rates with word-of-mouth effects
    - Late campaign: Lower rates as market saturation approaches
    """
    
    current = _parse_date(current_date)
    
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
                tickets_count=1
            )
            from .generate_custom_order import generate_customer_order
            new_order = generate_customer_order(new_customer, current_date)
            new_customer.historical_purchase_frequency.append(new_order)
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
    saturation_factor = max(CUSTOMER_ACQUISITION_SATURATION_MIN_FACTOR, 1.0 - (existing_customers_count / MAX_CUSTOMER_LIMIT))
    
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
    
    # Determine number of customers to acquire using binomial distribution
    # This models multiple independent acquisition events per day
    customers_to_acquire = 0
    
    # Try to acquire customers up to the maximum per day
    for attempt in range(MAX_CUSTOMERS_PER_DAY):
        if random.random() <= acquisition_probability:
            customers_to_acquire += 1
        else:
            # Stop trying if we fail to acquire one (realistic behavior)
            break
    
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
            tickets_count=1
        )
        from .generate_custom_order import generate_customer_order
        new_order = generate_customer_order(new_customer_data, current_date)
        new_customer_data.historical_purchase_frequency.append(new_order)
        new_customers_data.append(new_customer_data)
    
    return new_customers_data
