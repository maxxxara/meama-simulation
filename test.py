from mesa import Model
from config import CAMPAIGN_START
from datetime import datetime

def get_daily_prize(current_date: datetime) -> dict:
  current_day = current_date.day
  current_month = current_date.month
  day_of_week = current_date.strftime("%A")
  if current_month == 10 and current_day == 15:
    return {
      "prize": "BMW M4",
      "campaign_impact_increase": 0.2
    }
  if current_month == 11 and current_day == 30:
    return {
      "prize": "CyberTruck",
      "campaign_impact_increase": 0.0
    }
  if day_of_week == "Monday":
    return {
      "prize": "1000 GEL",
      "campaign_impact_increase": 0.5
    }
  elif day_of_week == "Tuesday":
    return {
      "prize": "1500 GEL",
      "campaign_impact_increase": 0.5
    }
  elif day_of_week == "Wednesday":
    return {
      "prize": "2000 GEL",
      "campaign_impact_increase": 0.6
    }
  elif day_of_week == "Thursday":
    return {
      "prize": "3000 GEL",
      "campaign_impact_increase": 0.7
    }
  elif day_of_week == "Friday":
    return {
      "prize": "3500 GEL",
      "campaign_impact_increase": 0.7
    }
  else:
    return {
      "prize": None,
      "campaign_impact_increase": 0.0
    }



class CustomerModel(Model):
    """A simulation that shows behavior of customer agents in a campaign environment."""

    def __init__(
        self, n=20, width=20, height=20, seed=None
    ):
        """Initialize the model.

        Args:
            n: Number of agents,
            width: Grid width.
            height: Grid heights.
            seed : Random seed for reproducibility.
        """
        super().__init__(seed=seed)
        self.num_agents = n
        self.current_date = CAMPAIGN_START

        # CustomerAgent.create_agents(
        #     model=self,
        #     n=self.num_agents,
        #     cell=self.random.choices(self.grid.all_cells.cells, k=self.num_agents),
        # )

    def step(self):
        # Get current day from the current_date
        print(get_daily_prize(self.current_date))
        pass


test = CustomerModel()
test.step()