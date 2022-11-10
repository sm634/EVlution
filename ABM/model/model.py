from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid,ContinuousSpace
from mesa.datacollection import DataCollector
from .agent import OPS
import numpy as np
import pandas as pd
import datetime
import yaml

class EV_model(Model):
    """A simple model of an economy where agents exchange currency at random.

    All the agents begin with one unit of currency, and each time step can give
    a unit of currency to another agent. Note how, over time, this produces a
    highly skewed distribution of wealth.
    """

    def __init__(self, **kwargs):

        # Read in configuration files from yaml. If any additional configs then will overwrite base
        self.read_configs(kwargs)

        # Read in Model level data
        self.date = pd.to_datetime(self.start_date)
        OPS_data = pd.read_csv(self.OPS_data_file, dtype={'EV_num':'int','EV_sat':'float'})
        load_curve = pd.read_csv(self.pop_load_base_file).set_index('time')
        EV_load_base = pd.read_csv(self.EV_load_base_file).set_index('time')
        self.day=0
        self.total_load_curve = pd.DataFrame()
        
        # Set Data Collection Modules
        self.datacollector = DataCollector(
            model_reporters = self.cfg['output']['model_reporters'], 
            agent_reporters = self.cfg['output']['agent_reporters']
        )
        model_rep_hours = dict(zip([str(x) for x in np.arange(24)],[str(x) for x in np.arange(24)]))
        self.datacollector_hours = DataCollector(
            model_reporters=model_rep_hours
        )

        
        # Create agents
        self.num_agents = len(OPS_data)
        self.schedule = RandomActivation(self)
        for i,row in OPS_data.iterrows():
            a = OPS(i, self, row, load_curve, EV_load_base)
            self.schedule.add(a)

        self.running = True
        self.collect()
        self.datacollector.collect(self)
        self.datacollector_hours.collect(self)

    def read_configs(self,kwargs):
        """ Read in configuation parameters from file given to set up model and agents"""

        # firstly read in config file if given, else take base_config.yml 
        if 'cfg' in kwargs.keys():
            cfg_file = kwargs['cfg']
        else:
            cfg_file = 'configs/base_cfg.yml'
        
        with open(cfg_file,'r') as ymlfile:
            self.cfg = yaml.safe_load(ymlfile)
        
        # take model_params from config file and assign them as attributes to model class
        for k,v in self.cfg['model_params'].items():
            setattr(self,k,v)
        
        # any additional key word arguments given in modle run instance will overwrite any params from the config file.
        # this is how we can use the vis tool to update params
        for k,v in kwargs.items():
            setattr(self,k,v)

    def step(self):
        self.schedule.step()

        self.collect()
        self.total_load_curve = pd.concat([self.total_load_curve,self.load_curve],ignore_index=True)
        # collect data
        self.datacollector.collect(self)
        self.datacollector_hours.collect(self)
        self.day+=1
        self.date += datetime.timedelta(days=1)

    def collect(self):
        self.tot_EVs = 0 
        self.total_daily_use = 0 
        self.pop_daily_use = 0 
        self.ev_daily_use = 0
        self.tot_pop = 0
        load_curve_list = []
        for agent in self.schedule.agents:
            load_curve_list.append(agent.load_curve)
            self.tot_pop += agent.Pop
            self.tot_EVs += agent.EV_num
            self.total_daily_use += agent.total_daily_use
            self.pop_daily_use += agent.pop_daily_use
            self.ev_daily_use += agent.ev_daily_use
        
        self.tot_EV_sat = self.tot_EVs / self.tot_pop
        self.load_curve = pd.concat(load_curve_list,axis=1).reset_index()
        self.load_curve['Total'] = self.load_curve.sum(axis=1)
        self.load_curve['Date'] = self.day

        for k,v in self.load_curve['Total'].to_dict().items():
            setattr(self,str(k),v)

    def run_model(self, n):
        for i in range(n):
            self.step()
                

