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
    if len(customers) == 100:
        break
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

model = CustomerModel(customers=customers)

model.run_full_campaign()

data = model.datacollector.get_model_vars_dataframe()

# Print model statistics
print("=== MODEL STATISTICS ===")
print(f"Received Orders Count: {model.received_orders_count}")
print(f"Generated Revenue: {model.generated_revenue}")
print(f"New Customers Count: {model.new_customers_count}")
print()

# Find customers with prize wins
print("=== CUSTOMERS WITH PRIZE WINS ===")
customers_with_prizes = []
for agent in model.agents:
    # Check if this is a CustomerAgent and has prize wins
    if isinstance(agent, CustomerAgent) and len(agent.prize_wins) > 0:
        customers_with_prizes.append({
            'customer_id': agent.customer_id,
            'email': agent.email,
            'prize_wins': agent.prize_wins,
            'prize_count': len(agent.prize_wins),
            'tickets_count': agent.tickets_count
        })

if customers_with_prizes:
    for customer in customers_with_prizes:
        print(f"Customer ID: {customer['customer_id']}")
        print(f"Email: {customer['email']}")
        print(f"Prizes Won: {customer['prize_wins']}")
        print(f"Tickets Count: {customer['tickets_count']}")
        print("-" * 40)
else:
    print("No customers have won prizes yet.")
print()

# Generate Excel report
print("=== GENERATING EXCEL REPORT ===")
excel_file_path = generate_campaign_excel_report(model)
print(f"Excel report saved to: {excel_file_path}")
print()
