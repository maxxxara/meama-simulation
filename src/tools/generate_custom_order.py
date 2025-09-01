import random
from datetime import datetime
from collections import Counter
import json
from typing import Union, Dict, Any
from config import (
    CAMPAIGN_START, CAMPAIGN_END,
    DEFAULT_NEW_CUSTOMER_ORDER_VALUE, CAMPAIGN_VALUE_MULTIPLIER_FACTOR,
    MINIMUM_ORDER_VALUE,MAXIMUM_ITEMS_PER_ORDER,
    MINIMUM_PRICE_RANGE, MAXIMUM_PRICE_RANGE, DEFAULT_ITEMS_PER_ORDER,
    BASE_CAMPAIGN_IMPACT_FACTOR
)
from ..models import Customer, Order, OrderLine
from .tools import generate_campaign_impact_factor

def generate_customer_order(customer_data: Union[Customer, Dict[str, Any]], current_date: Union[str, datetime]) -> Order:
    """
    Generates a realistic order for a customer based on their historical purchasing patterns.
    
    This function analyzes the customer's purchase history to predict:
    - What products they're likely to buy
    - How many items they'll order
    - The total order value
    - Campaign-related behavior changes
    
    Arguments:
    customer_data (Customer or dict): Customer data with historical_purchase_frequency, average_order_value, etc.
    current_date (str or datetime): Current simulation date (format: "2025-10-15" or datetime object)
    
    Returns:
    GeneratedOrder: Generated order with validated structure
    
    Raises:
    ValueError: If customer_data is invalid or current_date is invalid
    """
    
    # Validate input parameters
    if isinstance(customer_data, dict):
        try:
            customer = Customer(**customer_data)
        except Exception as e:
            raise ValueError(f"Invalid customer_data: {e}")
    elif isinstance(customer_data, Customer):
        customer = customer_data

   
    # Convert string dates to datetime objects if needed
    def parse_date(date_input):
        if isinstance(date_input, str):
            if 'T' in date_input:
                dt = datetime.fromisoformat(date_input.replace('Z', '+00:00'))
                # Convert to timezone-naive by removing timezone info
                return dt.replace(tzinfo=None)
            else:
                return datetime.strptime(date_input, "%Y-%m-%d")
        elif hasattr(date_input, 'tzinfo') and date_input.tzinfo is not None:
            # If it's a timezone-aware datetime, make it naive
            return date_input.replace(tzinfo=None)
        return date_input
    
    current_date = parse_date(current_date)
    historical_orders = customer.historical_purchase_frequency
    
    # Step 1: Analyze customer's product preferences
    product_preferences = _analyze_product_preferences(historical_orders)
    
    # Step 2: Determine order value range based on history and campaign effects
    target_order_value = _calculate_target_order_value(customer, current_date)
    
    # Step 3: Generate order lines based on preferences and target value
    order_lines_data = _generate_order_lines(product_preferences, target_order_value, current_date)
    
    # Step 4: Convert order lines to OrderLine objects
    order_lines = []
    for line_data in order_lines_data:
        order_line = OrderLine(
            product_name=line_data['product_name'],
            product_price=line_data['product_price'],
            quantity=line_data['quantity']
        )
        order_lines.append(order_line)
    
    # Step 5: Calculate actual total spent
    actual_total = sum(line.product_price * line.quantity for line in order_lines)
    
    # Step 6: Generate unique order ID (timestamp-based for simulation)
    order_id = int(current_date.timestamp() * 1000) + random.randint(1000, 9999)
    
    # Step 7: Create and return GeneratedOrder
    generated_order = Order(
        order_id=order_id,
        total_spent=round(actual_total, 2),
        order_date=current_date.isoformat(),
        order_lines=order_lines
    )
    
    return generated_order



# generate_customer_order helper
def _analyze_product_preferences(historical_orders):
    """
    Analyzes customer's historical orders to determine product preferences.
    
    Returns:
    dict: Product preference data with categories, favorite products, and patterns
    """
    
    if not historical_orders:
        return _get_default_product_preferences()
    
    # Collect all products bought by the customer
    all_products = []
    product_quantities = Counter()
    product_frequency = Counter()
    category_preferences = Counter()
    price_ranges = []
    
    for order in historical_orders:
        order_lines = order.order_lines
        for line in order_lines:
            product_name = line.product_name.strip()
            price = line.product_price
            quantity = line.quantity
            
            if not product_name or product_name == 'Unknown Product' or price is None:
                continue
                
            all_products.append(product_name)
            product_quantities[product_name] += quantity
            product_frequency[product_name] += 1
            price_ranges.append(price)
            
            # Categorize products
            category = _categorize_product(product_name)
            category_preferences[category] += quantity
    
    # Get most preferred products (top 70% by frequency)
    total_frequency = sum(product_frequency.values())
    preferred_products = []
    for product, freq in product_frequency.most_common():
        if len(preferred_products) < max(3, int(len(product_frequency) * 0.7)):
            preferred_products.append({
                'name': product,
                'frequency': freq,
                'preference_score': freq / total_frequency,
                'avg_quantity': product_quantities[product] / freq
            })
    
    return {
        'preferred_products': preferred_products,
        'category_preferences': dict(category_preferences),
        'avg_price_range': (min(price_ranges), max(price_ranges)) if price_ranges else (MINIMUM_PRICE_RANGE, MAXIMUM_PRICE_RANGE),
        'typical_items_per_order': len(all_products) / len(historical_orders) if historical_orders else DEFAULT_ITEMS_PER_ORDER
    }


# generate_customer_order helper
def _categorize_product(product_name):
    """
    Categorizes a product based on its name.
    This function is kept for backward compatibility but categories are now primarily
    sourced from the product catalog JSON file.
    """
    name_lower = product_name.lower()
    
    # Coffee varieties/origins
    if any(keyword in name_lower for keyword in ['ბრაზილია', 'გვატემალა', 'ეთიოპია', 'კოლუმბია', 'ელ-სალვადორი']):
        return 'coffee_origin'
    
    # Flavored coffee
    if any(keyword in name_lower for keyword in ['კარამელი', 'ვანილი', 'ტყის თხილი', 'მაკაპუნო', 'შოკოლად']):
        return 'flavored_coffee'
    
    # Colored/numbered varieties
    if any(keyword in name_lower for keyword in ['მწვანე', 'ლურჯი', 'წითელი', 'იასამნისფერი', 'ბურგუნდი', 'ყვითელი']):
        return 'coffee_blend'
    
    # Cups and accessories
    if any(keyword in name_lower for keyword in ['ჭიქა', 'ჰოლდერი', 'მეტალის', 'ფაიფურის']):
        return 'accessories'
    
    # Vending machine items
    if 'vending' in name_lower or 'ვენდინგ' in name_lower:
        return 'vending'
    
    # Special products
    if any(keyword in name_lower for keyword in ['meama', 'მეამა', 'პაკეტი']):
        return 'subscription'
    
    # Instant/ground coffee
    if 'ნალექიანი' in name_lower:
        return 'instant_coffee'
    
    # Default category
    return 'other'


# generate_customer_order helper
def _get_default_product_preferences():
    """
    Returns default product preferences from the product catalog JSON file.
    """
    try:
        with open('data/analysis/product_catalog.json', 'r', encoding='utf-8') as f:
            product_catalog = json.load(f)
        
        # Convert catalog format to preference format
        default_products = []
        category_preferences = {}
        
        for product in product_catalog:
            default_products.append({
                'name': product['name'],
                'frequency': product['frequency'],
                'preference_score': product['preference_score'],
                'avg_quantity': product['avg_quantity'],
                'avg_price': product['avg_price']
            })
            
            # Aggregate category preferences
            category = product['category']
            if category not in category_preferences:
                category_preferences[category] = 0
            category_preferences[category] += product['frequency']
        
        # Calculate price range
        prices = [p['avg_price'] for p in product_catalog if p['avg_price'] > 0]
        avg_price_range = (min(prices), max(prices)) if prices else (MINIMUM_PRICE_RANGE, MAXIMUM_PRICE_RANGE)
        
        # Calculate typical items per order
        total_frequency = sum(p['frequency'] for p in product_catalog)
        typical_items = total_frequency / len(product_catalog) if product_catalog else 2
        
        return {
            'preferred_products': default_products,
            'category_preferences': category_preferences,
            'avg_price_range': avg_price_range,
            'typical_items_per_order': typical_items
        }
        
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # Fallback to basic defaults if file is not available
        return {
            'preferred_products': [],
            'category_preferences': {},
            'avg_price_range': (MINIMUM_PRICE_RANGE, MAXIMUM_PRICE_RANGE),
            'typical_items_per_order': DEFAULT_ITEMS_PER_ORDER
        }


# generate_customer_order helper
def _calculate_target_order_value(customer: Customer, current_date):
    """
    Calculates the target order value based on customer history and campaign effects.
    """
    
    # Get base order value from customer history
    avg_order_value = customer.average_order_value
    historical_orders = customer.historical_purchase_frequency
    
    if avg_order_value <= 0 or not historical_orders:
        # Default for new customers
        base_value = DEFAULT_NEW_CUSTOMER_ORDER_VALUE
    else:
        base_value = avg_order_value
    
    # Apply campaign effects # Disable campaign
    # campaign_factor = generate_campaign_impact_factor(BASE_CAMPAIGN_IMPACT_FACTOR, 0, current_date)
    
    # Campaign effect on order value (not just frequency) # Disable campaign
    # During campaign, customers might spend 10-30% more per order
    # if campaign_factor > 1.0:
    #     value_multiplier = 1.0 + ((campaign_factor - 1.0) * CAMPAIGN_VALUE_MULTIPLIER_FACTOR)  # configurable % of frequency boost applies to value
    # else:
    value_multiplier = 1.0
    
    target_value = base_value * value_multiplier
    
    # Add some randomness (±20%)
    randomness = random.uniform(0.8, 1.2)
    target_value *= randomness
    
    return max(target_value, MINIMUM_ORDER_VALUE)  # Minimum order value


# generate_customer_order helper
def _generate_order_lines(product_preferences, target_value, current_date):
    """
    Generates realistic order lines based on preferences and target order value.
    """
    
    preferred_products = product_preferences['preferred_products']
    target_items = max(1, int(product_preferences['typical_items_per_order']))
    
    # Add some randomness to number of items
    num_items = max(1, int(target_items + random.normalvariate(0, 0.5)))
    num_items = min(num_items, MAXIMUM_ITEMS_PER_ORDER)  # Cap at reasonable maximum
    
    order_lines = []
    remaining_value = target_value
    
    for i in range(num_items):
        # Choose product based on preferences
        if preferred_products and random.random() < 0.7:  # configurable chance to pick preferred
            # Weight selection by preference scores
            weights = [p['preference_score'] for p in preferred_products]
            selected_product = random.choices(preferred_products, weights=weights)[0]
            
            product_name = selected_product['name']
            base_quantity = max(1, int(selected_product['avg_quantity']))
            
            # Get price from product name (simplified pricing model)
            price = _get_product_price(product_name, current_date)
            
        else:
            # Pick a random product from default catalog
            product_name, price = _get_random_product(current_date)
            base_quantity = 1
        
        # Determine quantity based on remaining budget
        max_affordable_qty = max(1, int(remaining_value / price)) if price > 0 else 1
        quantity = min(base_quantity + random.randint(0, 1), max_affordable_qty)
        
        # Ensure we don't overspend too much on early items if we have more items to add
        if i < num_items - 1:
            max_spend_on_this_item = remaining_value * 0.6  # Don't spend more than configurable % on one item
            max_qty_by_budget = int(max_spend_on_this_item / price) if price > 0 else 1
            quantity = min(quantity, max(1, max_qty_by_budget))
        
        order_lines.append({
            'product_name': product_name,
            'product_price': price,
            'quantity': quantity
        })
        
        remaining_value -= (price * quantity)
        
        # Stop if we've spent most of our budget
        if remaining_value <= MINIMUM_ORDER_VALUE:
            break
    
    return order_lines


# generate_customer_order helper
def _get_product_price(product_name, current_date):
    """
    Returns product price from the product catalog or calculates based on product type.
    """
    try:
        with open('data/analysis/product_catalog.json', 'r', encoding='utf-8') as f:
            product_catalog = json.load(f)
        
        # Find the product in the catalog
        for product in product_catalog:
            if product['name'] == product_name:
                base_price = product['avg_price']
                
                # Campaign period might have special pricing
                if isinstance(current_date, str):
                    if 'T' in current_date:
                        dt = datetime.fromisoformat(current_date.replace('Z', '+00:00'))
                        current = dt.replace(tzinfo=None)
                    else:
                        current = datetime.strptime(current_date, "%Y-%m-%d")
                elif hasattr(current_date, 'tzinfo') and current_date.tzinfo is not None:
                    current = current_date.replace(tzinfo=None)
                else:
                    current = current_date
                is_campaign = CAMPAIGN_START <= current <= CAMPAIGN_END
                
                return round(base_price, 2)
        
        # If product not found in catalog, use fallback pricing
        raise ValueError(f"Product {product_name} not found in catalog")
        
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        raise ValueError(f"Product {product_name} not found in catalog")

# generate_customer_order helper
def _get_random_product(current_date):
    """
    Returns a random product from the product catalog.
    """
    try:
        with open('data/analysis/product_catalog.json', 'r', encoding='utf-8') as f:
            product_catalog = json.load(f)
        
        # Filter out products with 0 frequency or 0 price
        valid_products = [
            p for p in product_catalog
            if p.get('frequency', 0) > 0 and p.get('avg_price', 0) > 0
        ]

        if not valid_products:
            # Fallback to basic defaults if no valid products found
            raise ValueError("No valid products found in catalog")

        # Weight selection by frequency
        weights = [p['frequency'] for p in valid_products]
        selected_product = random.choices(valid_products, weights=weights)[0]
        
        product_name = selected_product['name']
        price = _get_product_price(product_name, current_date)

        return product_name, price
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # Fallback to basic defaults if file is not available
        raise ValueError("No valid products found in catalog")
    


# print(result)