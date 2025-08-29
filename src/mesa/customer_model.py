from mesa import Model
from mesa.experimental.cell_space import OrthogonalMooreGrid
from .customer_agent import CustomerAgent
from mesa import DataCollector
from datetime import datetime, timedelta
from config import CAMPAIGN_START, CAMPAIGN_END
from ..tools.get_prizes import get_daily_prize, get_prize_winner
from ..models import Customer
from mesa.agent import AgentSet

class CustomerModel(Model):
    """A simulation that shows behavior of customer agents in a campaign environment."""

    def __init__(
        self, customers: list[Customer], seed: int | None = None
    ):
        """Initialize the model.

        Args:
            n: Number of agents,
            width: Grid width.
            height: Grid heights.
            seed : Random seed for reproducibility.
        """
        super().__init__(seed=seed)
        self.customers = customers
        self.new_customers_count: int = 0
        self.generated_revenue: float = 0.0
        self.received_orders_count: int = 0
        self.current_date = CAMPAIGN_START
        for customer in self.customers:
            self.agents.add(CustomerAgent(self, customer))
        self.datacollector = DataCollector(
            model_reporters={
                "new_customers_count": "new_customers_count",
                "generated_revenue": "generated_revenue",
                "received_orders_count": "received_orders_count"
            },
            agent_reporters={
                "ticketsCount": "ticketsCount",
                "campaign_impact_factor": "campaign_impact_factor",
                "hasWonImpactFactor": "hasWonImpactFactor",
                "prize_wins": "prize_wins",
                "new_order_count": "new_order_count"
            }
        )

    def step(self):
        """Run the simulation for ONE day only."""
        if self.current_date <= CAMPAIGN_END:
            print(f"Running simulation for {self.current_date} - Current Revenue: {self.generated_revenue}")
            self.new_day()
            return True
        return False

    def run_full_campaign(self):
        """Run the simulation for the entire campaign period."""
        while self.current_date <= CAMPAIGN_END:
            self.step()

    def new_day(self):
        daily_prize = get_daily_prize(self.current_date)
        if daily_prize is not None:
            prize_winner = get_prize_winner(self.customers)

            prize_winner_agent = self.agents.select(
                lambda agent: isinstance(agent, CustomerAgent) and agent.customer_id == prize_winner.id
            )
            if len(prize_winner_agent) > 0:
                winner = list(prize_winner_agent)[0]
                if isinstance(winner, CustomerAgent):
                    winner.campaign_impact_factor = winner.campaign_impact_factor + daily_prize.campaign_impact_increase
                    winner.hasWonImpactFactor = winner.hasWonImpactFactor + daily_prize.campaign_impact_increase
                    winner.prize_wins.append(daily_prize.prize)

        self.agents.do("step")
        self.datacollector.collect(self)
        self.current_date += timedelta(days=1)

