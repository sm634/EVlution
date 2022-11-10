from mesa.visualization.ModularVisualization import ModularServer
from .model import EV_model

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule,BarChartModule
from mesa.visualization.UserParam import UserSettableParameter
# from .SimpleContinuousModule import SimpleCanvas
import numpy as np

 
# def agent_portrayal(agent):
#     portrayal = {"Shape": "circle", "Filled": "true", "r": 2}

#     if agent.wealth > 0:
#         portrayal["Color"] = "red"
#         portrayal["Layer"] = 0
#     else:
#         portrayal["Color"] = "grey"
#         portrayal["Layer"] = 1
#         portrayal["r"] = 2
#     return portrayal


# grid = SimpleCanvas(agent_portrayal, 500, 500)
chart = ChartModule(
    [{"Label": "pop_daily_use", "Color": "red"},
     {"Label": "ev_daily_use", "Color": "blue"}], data_collector_name="datacollector"
)

hour_labs = [{'Label':str(x), "Color": "#0000FF"} for x in np.arange(24)]

barchart = BarChartModule(
    hour_labs, data_collector_name="datacollector_hours"
)

model_params = {
    "ev_growth": UserSettableParameter(
        "slider",
        "ev_growth",
        0.005,
        0.001,
        0.05,
        0.001,
        description="Choose how many agents to include in the model",
    ),
    "pop_growth": UserSettableParameter(
        "slider",
        "pop_growth",
        0.0005,
        0,
        0.01,
        0.0001,
        description="Choose how many agents to include in the model",
    )
}

server = ModularServer(EV_model, [ chart,barchart], "Money Model", model_params)
server.port = 8521
