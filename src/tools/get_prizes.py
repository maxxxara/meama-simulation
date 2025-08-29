from datetime import datetime
from pydantic import BaseModel
from ..models import Customer
import random

class Prize(BaseModel):
  prize: str 
  campaign_impact_increase: float

def get_daily_prize(current_date: datetime) -> Prize | None:
  current_day = current_date.day
  current_month = current_date.month
  day_of_week = current_date.strftime("%A")
  if current_month == 10 and current_day == 15:
    return Prize(
      prize="BMW M4",
      campaign_impact_increase=0.2
    )
  if current_month == 11 and current_day == 30:
    return Prize(
      prize="CyberTruck",
      campaign_impact_increase=0.0
    )
  if day_of_week == "Monday":
    return Prize(
      prize="1000 GEL",
      campaign_impact_increase=0.5
    )
  elif day_of_week == "Tuesday":
    return Prize(
      prize="1500 GEL",
      campaign_impact_increase=0.5
    )
  elif day_of_week == "Wednesday":
    return Prize(
      prize="2000 GEL",
      campaign_impact_increase=0.6
    )
  elif day_of_week == "Thursday":
    return Prize(
      prize="3000 GEL",
      campaign_impact_increase=0.7
    )
  elif day_of_week == "Friday":
    return Prize(
      prize="3500 GEL",
      campaign_impact_increase=0.7
    )
  else:
    return None


def get_prize_winner(customers: list[Customer]) -> Customer:
  customers = [customer for customer in customers if customer.tickets_count > 0]

  return random.choice(customers)