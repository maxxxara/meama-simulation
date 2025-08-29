from datetime import datetime

CAMPAIGN_START = datetime(2025, 9, 1) # September 1, 2025
CAMPAIGN_END = datetime(2025, 11, 30) # November 30, 2025

BASE_CAMPAIGN_IMPACT_FACTOR = 1.3 # 30% base increase during campaign
CAMPAIGN_ENGAGEMENT_MULTIPLIER = 0.1 # Additional 10% per order during campaign
MAX_CAMPAIGN_IMPACT_FACTOR= 3.0 # Maximum impact factor

NEW_CUSTOMER_BASELINE_PROBABILITY = 0.05 # What is the probability of a new customer to place an order

CUSTOMER_ACQUISITION_AFTER_CAMPAIGN_END = 0.02 # What is the probability of a new customer to place an order after the campaign end
CUSTOMER_ACQUISITION_CAMPAIGN_BIAS = 0.08 # What is the probability of a new customer to place an order during the campaign
PROPORTION_OF_NEW_CUSTOMERS = 0.25 # 25% of the total customer limit

# Customer Acquisition Configuration
MAX_CUSTOMERS_PER_DAY = 5  # Maximum customers that can be acquired in one day

# Campaign Timing Factors
CUSTOMER_ACQUISITION_EARLY_CAMPAIGN_THRESHOLD = 0.2  # Campaign progress threshold for early excitement
CUSTOMER_ACQUISITION_EARLY_CAMPAIGN_BOOST = 1.5  # Boost factor during early campaign
CUSTOMER_ACQUISITION_LATE_CAMPAIGN_THRESHOLD = 0.8  # Campaign progress threshold for late urgency
CUSTOMER_ACQUISITION_LATE_CAMPAIGN_BOOST = 1.3  # Boost factor during late campaign

# Word-of-Mouth Configuration
CUSTOMER_ACQUISITION_WORD_OF_MOUTH_MAX_ENGAGEMENT = 5.0  # Maximum engagement score for word-of-mouth
CUSTOMER_ACQUISITION_WORD_OF_MOUTH_MULTIPLIER = 0.1  # Multiplier for word-of-mouth effect

# Market Saturation Configuration
MAX_CUSTOMER_LIMIT = 30000
CUSTOMER_ACQUISITION_SATURATION_MIN_FACTOR = 0.3  # Minimum saturation factor (30% effectiveness at max saturation)

# Day of Week Configuration
CUSTOMER_ACQUISITION_WEEKEND_BOOST = 1.2  # Boost factor for weekend acquisitions

# Order Generation Configuration
CAMPAIGN_VALUE_MULTIPLIER_FACTOR = 0.5  # How much of campaign frequency boost applies to order value
MINIMUM_ORDER_VALUE = 5.0  # Minimum order value threshold
MAXIMUM_ITEMS_PER_ORDER = 7  # Cap on number of items in a single order
PRODUCT_PREFERENCE_THRESHOLD = 0.7  # Top 70% of products by frequency considered preferred

# Price ranges when user do not have any order history
MINIMUM_PRICE_RANGE = 20.0  # Minimum price range for new customers
MAXIMUM_PRICE_RANGE = 30.0  # Maximum price range for new customers
DEFAULT_ITEMS_PER_ORDER = 2  # Default items per order for new customers
DEFAULT_NEW_CUSTOMER_ORDER_VALUE = 35.0  # Default order value for customers with no history