from mesa.visualization.ModularVisualization import ModularServer
from .model import EVSpaceModel

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from .SimpleContinuousModule import SimpleCanvas

"""
    Sever file sets up the online visualisation in a localhost window. 
    agent_portrayal: sets up how the grid looks based on the Simple Canvas module 
    grid: creates a plot based on portrayal instance
    Charts: Then define which charts to display based on the model vars dataframe
    model_params: then defines the adjustable user parameters in the window
    server: creates the window in the local host
"""
 
def agent_portrayal(agent):
    portrayal = {"Shape": "circle", "Filled": "true", "r": 2}
    if agent.Type == 'CP':
        portrayal["Shape"] = "rect"
        portrayal["w"] = 0.05
        portrayal["h"] = 0.05
        portrayal["Filled"] = False
        if agent.full:
            portrayal["Color"] = "red"
        else:
            portrayal["Color"] = "Black"
        
    else:
        portrayal["r"] = 2

        # todo fix arrowhead shape in js 
        # portrayal["Shape"] = "arrowHead"
        # portrayal["scale"] = 1
        # portrayal["heading_x"] = 0 #agent.dx
        # portrayal["heading_y"] = 1 #agent.dy
        
        if agent.charge > 0.5:
            portrayal["Color"] = "green"
            portrayal["Layer"] = 1
        else:
            portrayal["Color"] = "red"
            portrayal["Layer"] = 1

        if agent.unique_id == 0:
            portrayal["Layer"] = 2
            portrayal["r"] = 10

    return portrayal

grid = SimpleCanvas(agent_portrayal, 500, 500)
chart = ChartModule(
    [{"Label": "dead_cars", "Color": "#0000FF"}], data_collector_name="datacollector"
)
chart2 = ChartModule(
    [{"Label": "av_charge", "Color": "#0000FF"}], data_collector_name="datacollector"
)
chart3 = ChartModule(
    [{"Label": "completed_trip", "Color": "#0000FF"}], data_collector_name="datacollector"
)

model_params = {
    "model_name": UserSettableParameter('number', value=0, description="Model Name"),
    "N": UserSettableParameter(
        "slider", #type of button
        "Number of agents", # name
        100, # inital
        10, # min
        1000, # max
        10, # increment
        description="Choose how many agents to include in the model",
    ),
    "N_Charge": UserSettableParameter(
        "slider", #type of button
        "Number of Charge Points", # name
        10, # inital
        1, # min
        50, # max
        1, # increment
        description="Choose how many Charge points to include in the model",
    ),
    "CP_loc": UserSettableParameter(
        "choice", 
        'Charge Point Distribution', 
        value='random',
        choices=['random', 'uniform','inputs/CP_locs.csv'],
        description="How to distribute charge points",
    ),
    "POIs": UserSettableParameter(
        "choice", 
        'POIs', 
        value='None',
        choices=['None','inputs/POIs.csv'],
        description="How to distribute EV POIs",
    ),
    "MoveType": UserSettableParameter(
        "choice", 
        'Movement Type', 
        value='loc',
        choices=['loc', 'random'],
        description="Is movement location based or fully random",
    ),
    "speed": UserSettableParameter(
        "slider",
        "Speed of Movement",
        .2,
        0,
        2,
        0.1,
        description="Speed agents can move each step",
    ),
    "discharge_rate": UserSettableParameter(
        "slider",
        "discharge_rate",
        0.01,
        0.01,
        0.2,
        0.01,
        description="discharge_rate",
    ),
    "width": UserSettableParameter(
        "slider", #type of button
        "width", # name
        10., # inital
        5., # min
        50., # max
        1., # increment
        description="width",
    ),
    "height": UserSettableParameter(
        "slider", #type of button
        "height", # name
        10., # inital
        5., # min
        50., # max
        1., # increment
        description="height",
    ),
}

server = ModularServer(EVSpaceModel, [grid, chart,chart2,chart3], "EV Model", model_params)
server.port = 8521
