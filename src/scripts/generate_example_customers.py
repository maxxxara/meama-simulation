#!/usr/bin/env python3
import json
import os

NUMBER_OF_CUSTOMERS = 10

input_file = "./data/customers.json"
output_file = "./data/customers.example.json"

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        customers = json.load(f)
    
    first_5_customers = customers[:NUMBER_OF_CUSTOMERS]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(first_5_customers, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully extracted first 5 customers from {input_file}")
    print(f"Written to {output_file}")
    print(f"Number of customers extracted: {len(first_5_customers)}")

except FileNotFoundError:
    print(f"Error: Could not find {input_file}")
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON in {input_file}: {e}")
except Exception as e:
    print(f"Error: {e}")
