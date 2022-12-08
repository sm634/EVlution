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
        portrayal["Layer"] = 3 
        portrayal["Filled"] = False
        if agent.full:
            portrayal["Color"] = "red"
        else:
            portrayal["Color"] = "Black"
        
    else:
        portrayal["r"] = 2
        
        if not agent.moving:
            if agent.last_location =='home':
                portrayal["Color"] = "red"
            if agent.last_location =='work':
                portrayal["Color"] = "green"
            if agent.last_location =='charge':
                portrayal["Color"] = "teal"
            if agent.last_location =='random':
                portrayal["Color"] = "pink"
        else:
            if agent.charge > 0.5:
                portrayal["Color"] = "blue"
                portrayal["Layer"] = 1
            else:
                portrayal["Color"] = "black"
                portrayal["Layer"] = 1

        if agent.large_id:
            portrayal["Layer"] = 5
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
    [{"Label": "av_moving", "Color": "blue"},
    {"Label": "av_home", "Color": "red"},
    {"Label": "av_work", "Color": "green"},
    {"Label": "av_random", "Color": "pink"},
        ], data_collector_name="datacollector"
)
chart4 = ChartModule(
    [{"Label": "charge_load", "Color": "#0000FF"}], data_collector_name="datacollector"
)

model_params = {
    "xx_model_title": UserSettableParameter('static_text', value="Model Parameters"),
    "cfg": UserSettableParameter(
        "choice", 
        'Configuration File', 
        value='None',
        choices=['configs/Toronto_cfg.yml', 'configs/east_box.yml','None','configs/Mississauga_cfg.yml','configs/Point_Edward_cfg.yml', 'configs/west_box.yml'],
        description="How to distribute EV POIs",
    ),
    "xx_ev_title": UserSettableParameter('static_text', value="Electric Vehical Parameters"),
    "EVP_num_agents": UserSettableParameter(
        "choice", 
        'Number of EV Agents', 
        value='base',
        choices=['base',100, 500, 1000, 2000],
        description="Number of EV agents to place on the Grid",
    ),
    "EVP_dist_per_step": UserSettableParameter(
        "choice", 
        'Distance EVs can move (km/h)', 
        value='base',
        choices=['base',1,5,10,25,50],
        description="Distance EVs can move in 1 hour step",
    ),
    "EVP_efficiency_rating": UserSettableParameter(
        "choice", 
        'Efficiency Rating (km/kWh)', 
        value='base',
        choices=['base',1,3,5,10],
        # description="How to distribute EV POIs",
    ),
    
    "xx_charge_title": UserSettableParameter('static_text', value="CP Parameters"),
    "ChargeP_CP_loc": UserSettableParameter(
        "choice", 
        'Charge Point Distribution', 
        value='base',
        choices=['base','random'],
        description="How to distribute charge points",
    ),
    "ChargeP_N_Charge": UserSettableParameter(
        "choice", 
        'If Random Distribution Number of Charge Points', 
        value='base',
        choices=['base',1,5,10,25,50,100],
    ),
}

server = ModularServer(EVSpaceModel, [grid,chart3,chart4, chart,chart2], "EVlution Electric Vehicle Simulation Model", model_params)
server.port = 8521
