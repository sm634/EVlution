from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid,ContinuousSpace
from .EVAgent import EVAgent
from .ChargePoint import ChargePoint
from .GridAgent import GridAgent
import numpy as np
import pandas as pd
import itertools

from .datacollection import DataCollector

def compute_gini(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    x = sorted(agent_wealths)
    N = model.num_agents
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return 1 + (1 / N) - 2 * B
    
def av_charge(model):
    agent_charges = [agent.charge for agent in model.schedule.agents]
    return sum(agent_charges)/len(agent_charges)

def dead_cars(model):
    dead_cars = 0
    for agent in model.schedule.agents:
        if agent.charge<=0:
            dead_cars += 1
    return dead_cars

class EVSpaceModel(Model):
    """ Electric Vehical Model, where cars drive around between locations then pull into charge points
    """

    def __init__(self, N=100, width=10., height=10., speed=1, N_Charge=10,discharge_rate=0.01,CP_loc='random', 
                    model_name = 0, MoveType = 'loc', charge_rate = 0.2, CP_capacity=10, grid_spacing = None,
                    POIs='None'):
                    
        """ initalisation of the model, set up agent space, agents and collection modules"""
        self.num_agents = N
        self.model_name = model_name
        self.MoveType = MoveType
        self.charge_rate = charge_rate
        tol = 0.01
        self.width =width
        self.height = height
        self.space = ContinuousSpace(width+tol, height+tol,False,x_min=-tol,y_min=-tol) # change to newtwork model with graph as road netowrk
        self.speed = speed
        self.completed_trip =0
        self.N_Charge = N_Charge

        # todo set up POI agents which EVs then choose which they want to go to
        if POIs != 'None':
            self.POIs = pd.read_csv(POIs).set_index('id')
            self.POIs['uses'] = 0
        else:
            self.POIs = []
            
        # set up EV agents
        self.schedule = RandomActivation(self)
        self.schedule_list = ['schedule']
        self.datacollector = DataCollector(schedule='schedule',
            model_reporters={"av_charge": av_charge,
                            "completed_trip": "completed_trip",
                            "dead_cars": dead_cars,}, 
            agent_reporters={"charge": "charge",
                            'last_location':'last_location',
                            'next_location':'next_location',
                            'pos':'pos'} # also could have deadline to work out if can get there one current charge
                            
        )
        for i in range(self.num_agents):
            a = EVAgent(i, self, speed, discharge_rate)
            self.schedule.add(a)
            # Add the agent to a random space
            self.space.place_agent(a, a.pos)
        self.datacollector.collect(self)

        #set up charging points
        self.schedule_CP = RandomActivation(self)
        self.schedule_list.append('schedule_CP')
        self.datacollector_CP = DataCollector(schedule='schedule_CP',
            agent_reporters={"cars_charging": "cars_charging",
                            'full':'full'}
        )
        self.gen_CPs(CP_loc, CP_capacity)
        self.datacollector_CP.collect(self)

        #set up grid points for analysis
        self.schedule_gridpoints = RandomActivation(self)
        # self.schedule_list.append('schedule_gridpoints')
        self.datacollector_gridpoints = DataCollector(schedule='schedule_gridpoints',
            agent_reporters={'pos':'pos',
                            "cars_passing": "cars_passing",
                            'X':'X','Y':'Y'}
        )
        if type(grid_spacing)==int:
            grid_locs_x = np.linspace(0, self.width, grid_spacing)
            grid_locs_y = np.linspace(0, self.height, grid_spacing)
            grid_locs = itertools.product(grid_locs_x, grid_locs_y) 
            radius = (self.width+self.height) / (2*grid_spacing)
            for i, pos in enumerate(grid_locs):
                a = GridAgent(i, self, pos, radius)
                self.schedule_gridpoints.add(a)
                # Add the agent to a random space
                self.space.place_agent(a, a.pos)
        self.schedule_gridpoints.step()
        self.datacollector_gridpoints.collect(self)
        
        self.running = True

    def gen_CPs(self, CP_loc, CP_capacity):
        # determine charge point locations, either uniform or randomly distribute
        if isinstance(CP_loc, pd.DataFrame):
            self.N_Charge = len(CP_loc)
            names = CP_loc.index
            x_pos = CP_loc['x'].values
            y_pos = CP_loc['y'].values
        elif '.csv' in CP_loc:
            CP_locs = pd.read_csv(CP_loc).set_index('id')
            self.N_Charge = len(CP_locs)
            names = CP_locs.index
            x_pos = CP_locs['x'].values
            y_pos = CP_locs['y'].values
        elif CP_loc == 'uniform':
            indices = np.arange(0, self.N_Charge, dtype=float) + 0.5
            r = np.sqrt(indices/self.N_Charge)
            theta = np.pi * (1 + 5**0.5) * indices
            x_pos = r*np.cos(theta) * self.width/2 + self.width/2
            y_pos = r*np.sin(theta) * self.height/2 + self.height/2
        else:
            x_pos = np.random.random(self.N_Charge) * self.width
            y_pos = np.random.random(self.N_Charge) * self.height
        
        charge_locs = list(zip(x_pos,y_pos))    

        # create and place charge points
        self.charge_locations = {}
        for i in range(self.N_Charge):
            name = str(i)+'_Charge'

            pos = charge_locs[i]
            a = ChargePoint(name, self, pos, CP_capacity)
            self.schedule_CP.add(a)

            # Add the agent to space
            self.space.place_agent(a, pos)
            self.charge_locations[name] = pos

    def step(self):
        """ This is the key model function which is run once each step. Here we loop through the agent schedule, which performs each agent step """
        self.completed_trip = 0 
        self.schedule.step()
        self.schedule_CP.step()
        self.schedule_gridpoints.step()
        self.collect()
    
    def collect(self):
        # collect data
        self.datacollector.collect(self) # collect agent and model information
        self.datacollector_CP.collect(self) # collect agent and model information
        self.datacollector_gridpoints.collect(self) # collect agent and model information
        # for agent in self.schedule.agents:
        #     if agent.Type == 'CP':

        if self.schedule.steps == 100:
            self.save()  # crude save technique for online models

    def run_model(self, n):
        """ if running offline model then can use this to run full model span """
        for i in range(n):
            self.step()

    def save(self):
        """ save out model/agent dataframes if given model name """
        if self.model_name != 0:
            mdf = self.datacollector.get_model_vars_dataframe()
            adf = self.datacollector.get_agent_vars_dataframe()
            
            mdf.to_csv('Data/mdf_{}.csv'.format(self.model_name))            
            adf.to_csv('Data/adf_{}.csv'.format(self.model_name))

            adf = self.datacollector_CP.get_agent_vars_dataframe()
            adf.to_csv('Data/adf_CP_{}.csv'.format(self.model_name))

            adf = self.datacollector_gridpoints.get_agent_vars_dataframe()
            adf.to_csv('Data/adf_GP_{}.csv'.format(self.model_name))