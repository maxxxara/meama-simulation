import seaborn as sns
from .customer_model import CustomerModel
from .customer_agent import CustomerAgent
from .excel_report_generator import generate_campaign_excel_report
import matplotlib.pyplot as plt
import json
from ..models import Customer
from datetime import datetime
import re
import os

# Get the project root directory (assuming this script is in src/mesa/)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_dir = os.path.join(project_root, "data")

# Ensure data directory exists
os.makedirs(data_dir, exist_ok=True)

print("=== LOADING CUSTOMERS ===")

with open("data/customers.json", "r") as f:
    customers_data = json.load(f)

customers : list[Customer] = []
for customer_data in customers_data:
    customers.append(Customer(
        id=customer_data["id"],
        email=customer_data["email"],
        created_at=datetime.strptime(customer_data["created_at"], "%Y-%m-%d %H:%M:%S.%f %z") if customer_data["created_at"] is not None else datetime.now(),
        historical_purchase_frequency=customer_data["historical_purchase_frequency"] if customer_data["historical_purchase_frequency"] is not None else [],
        historical_spending=customer_data["historical_spending"] if customer_data["historical_spending"] is not None else 0,
        average_order_value=customer_data["average_order_value"] if customer_data["average_order_value"] is not None else 0,
        total_orders=customer_data["total_orders"] if customer_data["total_orders"] is not None else 0,
        is_new_customer=False,
        tickets_count=1,
    ))

print(f"Customers loaded: {len(customers)}")
print()

print("=== STARTING SIMULATION ===")

model = CustomerModel(customers=customers)

model.run_full_campaign()

data = model.datacollector.get_model_vars_dataframe()

# Print model statistics
print("=== MODEL STATISTICS ===")
print(f"Received Orders Count: {model.received_orders_count}")
print(f"Generated Revenue: {model.generated_revenue}")
print(f"New Customers Count: {model.new_customers_count}")
print()

