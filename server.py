#!/usr/bin/env python3
"""
MEAMA Customer Simulation - Solara Server

This file can be run with: python -m solara run server.py --port=8521
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import solara
import pandas as pd
import plotly.express as px

from mesa.customer_model import CustomerModel
from models import Customer, Order, OrderLine


def load_customer_data(file_path: str = "data/customers.json") -> List[Customer]:
    """
    Load customer data from JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        customers = []
        for customer_data in data:
            # Convert order data to Order objects
            orders = []
            for order_data in customer_data.get('historical_purchase_frequency', []):
                order_lines = []
                for line_data in order_data.get('order_lines', []):
                    order_line = OrderLine(
                        product_name=line_data.get('product_name', ''),
                        product_price=line_data.get('product_price', 0.0),
                        quantity=line_data.get('quantity', 1)
                    )
                    order_lines.append(order_line)
                
                order = Order(
                    order_id=order_data.get('order_id', 0),
                    total_spent=order_data.get('total_spent', 0.0),
                    order_date=order_data.get('order_date', ''),
                    order_lines=order_lines
                )
                orders.append(order)
            
            customer = Customer(
                id=customer_data.get('id', 0),
                email=customer_data.get('email', ''),
                created_at=customer_data.get('created_at', ''),
                historical_purchase_frequency=orders,
                historical_spending=customer_data.get('historical_spending', 0.0),
                average_order_value=customer_data.get('average_order_value', 0.0),
                total_orders=customer_data.get('total_orders', 0),
                is_new_customer=customer_data.get('is_new_customer', False)
            )
            customers.append(customer)
        
        return customers
    except FileNotFoundError:
        print(f"⚠️ Customer data file not found: {file_path}")
        print("Using sample data instead...")
        return _generate_sample_customers()
    except Exception as e:
        print(f"❌ Error loading customer data: {e}")
        return _generate_sample_customers()


def _generate_sample_customers() -> List[Customer]:
    """
    Generate sample customer data for testing.
    """
    customers = []
    for i in range(100):  # Generate 100 sample customers
        # Create sample order
        order_line = OrderLine(
            product_name="Sample Coffee",
            product_price=25.0,
            quantity=1
        )
        
        order = Order(
            order_id=i + 1,
            total_spent=25.0,
            order_date="2025-08-01",
            order_lines=[order_line]
        )
        
        customer = Customer(
            id=i + 1,
            email=f"customer{i+1}@example.com",
            created_at="2025-01-01",
            historical_purchase_frequency=[order],
            historical_spending=25.0,
            average_order_value=25.0,
            total_orders=1,
            is_new_customer=False
        )
        customers.append(customer)
    
    return customers


# Global model instance
model = None


def run_simulation():
    """
    Run the simulation for a few steps.
    """
    global model
    if model and model.running:
        for _ in range(10):  # Run 10 steps
            if model.running:
                model.step()


def reset_simulation():
    """
    Reset the simulation.
    """
    global model
    customers = load_customer_data()
    model = CustomerModel(
        initial_customers=customers,
        start_date=datetime(2025, 8, 1),
        end_date=datetime(2025, 12, 31)
    )


# Initialize model
if model is None:
    customers = load_customer_data()
    model = CustomerModel(
        initial_customers=customers,
        start_date=datetime(2025, 8, 1),
        end_date=datetime(2025, 12, 31)
    )


# Create the main page
def Page():
    """
    Main simulation page.
    """
    solara.Title("MEAMA Customer Simulation")
    
    with solara.Column():
        solara.Markdown("# 🚀 MEAMA Customer Campaign Simulation")
        solara.Markdown("This simulation models customer behavior during the promotional campaign period.")
        
        # Control buttons
        with solara.Row():
            solara.Button("Run Simulation", on_click=run_simulation)
            solara.Button("Reset", on_click=reset_simulation)
        
        # Display summary
        if model and hasattr(model, 'total_revenue'):
            summary = model.get_simulation_summary()
            solara.HTML(f"""
            <div style="padding: 20px; background-color: #f5f5f5; border-radius: 8px;">
                <h3>Simulation Summary</h3>
                <p><strong>Total Revenue:</strong> ${summary['revenue_metrics']['total_revenue']:,.2f}</p>
                <p><strong>Campaign Revenue:</strong> ${summary['revenue_metrics']['campaign_revenue']:,.2f}</p>
                <p><strong>Campaign Lift:</strong> {summary['revenue_metrics']['campaign_lift_percent']:.1f}%</p>
                <p><strong>Total Customers:</strong> {summary['customer_metrics']['total_customers']}</p>
                <p><strong>New Customers:</strong> {summary['customer_metrics']['new_customers_acquired']}</p>
            </div>
            """)
        else:
            solara.Text("Simulation not started")
        
        # Display campaign metrics
        if model and hasattr(model, 'campaign_engagement_metrics'):
            metrics = model.campaign_engagement_metrics
            solara.HTML(f"""
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 20px;">
                <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h4>Total Orders</h4>
                    <p style="font-size: 24px; font-weight: bold; color: #007bff;">{metrics.total_orders}</p>
                </div>
                <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h4>Active Customers</h4>
                    <p style="font-size: 24px; font-weight: bold; color: #28a745;">{metrics.active_customers}</p>
                </div>
                <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h4>Avg Order Value</h4>
                    <p style="font-size: 24px; font-weight: bold; color: #ffc107;">${metrics.average_order_value:.2f}</p>
                </div>
            </div>
            """)
        
        # Display revenue chart if data exists
        if model and hasattr(model, 'daily_revenue') and model.daily_revenue:
            dates = pd.date_range(
                start=model.start_date,
                periods=len(model.daily_revenue),
                freq='D'
            )
            
            df = pd.DataFrame({
                'Date': dates,
                'Revenue': model.daily_revenue,
                'Orders': model.daily_orders if hasattr(model, 'daily_orders') else [0] * len(model.daily_revenue)
            })
            
            fig = px.line(df, x='Date', y=['Revenue', 'Orders'], title='Simulation Results')
            solara.FigurePlotly(fig)

