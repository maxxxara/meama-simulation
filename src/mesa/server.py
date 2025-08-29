import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from mesa.experimental.devs import ABMSimulator

from src.mesa.customer_model import CustomerModel
from src.mesa.customer_agent import CustomerAgent
from mesa.visualization import SolaraViz, make_space_component
from mesa.visualization.components.matplotlib_components import make_mpl_space_component
import solara
def agent_portrayal(agent):
    if isinstance(agent, CustomerAgent):
        return {
            "color": "red" if agent.wealth > 0 else "black",
            "size": 100, 
        }


def create_large_figure(ax):
    """Modify the figure to have larger size for better visibility."""
    fig = ax.figure
    fig.set_size_inches(10, 10)  # 12x12 inch figure
    return ax

model_params = {
    "n": {
        "type": "SliderInt",
        "value": 20,
        "label": "Number of agents:",
        "min": 10,
        "max": 100,
        "step": 1,
    },
    "width": {
        "type": "SliderInt",
        "value": 20,
        "label": "Width:",
        "min": 10,
        "max": 100,
        "step": 1,
    },
    "height": {
        "type": "SliderInt",
        "value": 20,
        "label": "Height:",
        "min": 10,
        "max": 100,
        "step": 1,
    },
}

model = CustomerModel()


simulator = ABMSimulator()



page = SolaraViz(
    model,
    components=[make_space_component(
        agent_portrayal,
        post_process=create_large_figure
    )],
    model_params=model_params,
    name="Customer Model",
)