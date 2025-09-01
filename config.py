from datetime import datetime

# === CAMPAIGN TOGGLE CONFIGURATION ===
# Set to False to simulate vanilla sales process without campaign effects
# Set to True to enable full campaign behavior (prizes, impact factors, enhanced acquisition)
ENABLE_CAMPAIGN_EFFECTS = True

CAMPAIGN_START = datetime(2025, 9, 1) # September 1, 2025
CAMPAIGN_END = datetime(2025, 11, 30) # November 30, 2025

BASE_CAMPAIGN_IMPACT_FACTOR = 1.3 # 30% base increase during campaign (up from 10%)
CAMPAIGN_ENGAGEMENT_MULTIPLIER = 0.15 # Additional 15% per order during campaign (up from 5%)
MAX_CAMPAIGN_IMPACT_FACTOR= 2.0 # Maximum impact factor (up from 1.5 for stronger campaigns)

NEW_CUSTOMER_BASELINE_PROBABILITY = 0.01 # What is the probability of a new customer to place an order (1% daily = ~30% monthly)

CUSTOMER_ACQUISITION_AFTER_CAMPAIGN_END = 0.001 # 0.1% daily probability after campaign (realistic baseline)
CUSTOMER_ACQUISITION_CAMPAIGN_BIAS = 0.01 # 1.0% daily probability during campaign (10x baseline for significant impact)
PROPORTION_OF_NEW_CUSTOMERS = 0.05 # 5% of the total customer limit (reduced from 25%)

# Customer Acquisition Configuration  
MAX_CUSTOMERS_PER_DAY = 5  # Maximum 5 customers per day during campaigns (increased from 2 for campaign impact)

# Campaign Timing Factors
CUSTOMER_ACQUISITION_EARLY_CAMPAIGN_THRESHOLD = 0.2  # Campaign progress threshold for early excitement
CUSTOMER_ACQUISITION_EARLY_CAMPAIGN_BOOST = 2.5  # 150% boost during early campaign for strong launch
CUSTOMER_ACQUISITION_LATE_CAMPAIGN_THRESHOLD = 0.8  # Campaign progress threshold for late urgency  
CUSTOMER_ACQUISITION_LATE_CAMPAIGN_BOOST = 2.0  # 100% boost during late campaign for urgency

# Word-of-Mouth Configuration
CUSTOMER_ACQUISITION_WORD_OF_MOUTH_MAX_ENGAGEMENT = 5.0  # Maximum engagement score for word-of-mouth
CUSTOMER_ACQUISITION_WORD_OF_MOUTH_MULTIPLIER = 0.05  # Reduced to 0.05 for realistic word-of-mouth effect

# Market Saturation Configuration
CUSTOMER_ACQUISITION_SATURATION_MIN_FACTOR = 0.5  # Minimum saturation factor (30% effectiveness at max saturation)

# Day of Week Configuration
CUSTOMER_ACQUISITION_WEEKEND_BOOST = 1.2  # Boost factor for weekend acquisitions

# Order Generation Configuration
CAMPAIGN_VALUE_MULTIPLIER_FACTOR = 0.2  # How much of campaign frequency boost applies to order value
MINIMUM_ORDER_VALUE = 5.0  # Minimum order value threshold
MAXIMUM_ITEMS_PER_ORDER = 7  # Cap on number of items in a single order
PRODUCT_PREFERENCE_THRESHOLD = 0.7  # Top 70% of products by frequency considered preferred

# Price ranges when user do not have any order history
MINIMUM_PRICE_RANGE = 20.0  # Minimum price range for new customers
MAXIMUM_PRICE_RANGE = 30.0  # Maximum price range for new customers
DEFAULT_ITEMS_PER_ORDER = 2  # Default items per order for new customers
DEFAULT_NEW_CUSTOMER_ORDER_VALUE = 35.0  # Default order value for customers with no history

# === ENHANCED PURCHASE BEHAVIOR FACTORS ===

# Customer Satisfaction Impact
SATISFACTION_LOW_THRESHOLD = 0.3  # Below this, customers are very unlikely to purchase
SATISFACTION_HIGH_THRESHOLD = 0.8  # Above this, customers get purchase boosts
SATISFACTION_DECAY_RATE = 0.02  # Daily satisfaction decay rate
SATISFACTION_RECOVERY_RATE = 0.05  # Recovery rate after time passes since negative experience

# Purchase Intent Modeling  
PURCHASE_INTENT_DECAY_RATE = 0.01  # Daily decay of purchase intent
PURCHASE_INTENT_BOOST_AFTER_BROWSE = 0.1  # Intent boost (simulated browsing behavior)
IMPULSE_PURCHASE_THRESHOLD = 0.2  # Below this intent level, only impulse purchases possible
PLANNED_PURCHASE_THRESHOLD = 0.7  # Above this, likely planned purchase behavior

# Seasonal and Interest Fluctuation
SEASONAL_BOOST_MONTHS = [11, 12, 1, 2]  # Holiday/New Year shopping months
SEASONAL_BOOST_FACTOR = 1.15  # 15% boost during seasonal months
SEASONAL_LOW_MONTHS = [6, 7, 8]  # Summer low activity months  
SEASONAL_LOW_FACTOR = 0.9  # 10% reduction during low months

# Economic/External Factors
ECONOMIC_SENTIMENT_FACTOR = 1.0  # Global economic sentiment (0.8-1.2 range)
WEEKEND_IMPULSE_BOOST = 1.1  # Weekend impulse purchase boost
PAYDAY_BOOST_DAYS = [1, 15]  # Days of month with payday boosts

# Product Interest Fluctuation
PRODUCT_INTEREST_DECLINE_RATE = 0.005  # Daily decline in product interest
PRODUCT_DISCOVERY_BOOST = 0.3  # Boost when "discovering" new products (simulated)

# Price Sensitivity Impact
HIGH_PRICE_SENSITIVITY_THRESHOLD = 0.7  # Above this, very price sensitive
LOW_PRICE_SENSITIVITY_THRESHOLD = 0.3  # Below this, price insensitive
PRICE_SENSITIVE_REDUCTION_FACTOR = 0.6  # Reduction for price-sensitive customers

# Brand Loyalty Impact
HIGH_BRAND_LOYALTY_THRESHOLD = 0.8  # Above this, strong brand loyalty
LOW_BRAND_LOYALTY_THRESHOLD = 0.3  # Below this, likely to churn
BRAND_LOYALTY_BOOST_FACTOR = 1.2  # Boost for loyal customers