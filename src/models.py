from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union
from datetime import datetime


class OrderLine(BaseModel):
    """Represents a single product line in an order."""
    product_name: str = Field(..., description="Name of the product")
    product_price: Optional[float] = Field(None, description="Price of the product")
    quantity: int = Field(..., ge=1, description="Quantity ordered")


class Order(BaseModel):
    """Represents a customer order."""
    order_id: int = Field(..., description="Unique order identifier")
    total_spent: float = Field(..., ge=0, description="Total amount spent on the order")
    order_date: str = Field(..., description="Order date in ISO format")
    order_lines: List[OrderLine] = Field(..., description="List of products in the order")


class Customer(BaseModel):
    """Represents a customer with their complete data."""
    id: int = Field(..., description="Unique customer identifier")
    email: str = Field(..., description="Customer email address")
    created_at: datetime = Field(..., description="Customer registration date")
    historical_purchase_frequency: List[Order] = Field(default_factory=list, description="Historical orders")
    historical_spending: float = Field(0.0, ge=0, description="Total historical spending")
    average_order_value: float = Field(0.0, ge=0, description="Average order value")
    total_orders: int = Field(0, ge=0, description="Total number of orders")
    is_new_customer: Optional[bool] = Field(False, description="Whether this is a new customer")
    tickets_count: int = Field(0, ge=0, description="Number of tickets")


class CampaignEngagementMetrics(BaseModel):
    """Represents the metrics of the campaign."""
    total_orders: int = Field(0, ge=0, description="Total number of orders")
    active_customers: int = Field(0, ge=0, description="Number of customers who placed orders during campaign")