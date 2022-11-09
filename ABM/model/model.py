from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid,ContinuousSpace
from mesa.datacollection import DataCollector
from .agent import OPS
import numpy as np
import pandas as pd
import datetime


class EV_model(Model):
    """A simple model of an economy where agents exchange currency at random.

    All the agents begin with one unit of currency, and each time step can give
    a unit of currency to another agent. Note how, over time, this produces a
    highly skewed distribution of wealth.
    """

    def __init__(self, pop_growth=0.0005, ev_growth=0.005, start_date = '2022-01-01',seasonal_fract=0,
                OPS_data='Data/OPS_data.csv',load_curve='Data/load_curve.csv',EV_load_base='Data/EV_load_base.csv', ):


        self.date = pd.to_datetime(start_date)
        OPS_data = pd.read_csv(OPS_data,dtype={'EV_num':'int','EV_sat':'float'})
        load_curve = pd.read_csv(load_curve).set_index('time') * 0.05
        EV_load_base = pd.read_csv(EV_load_base).set_index('time')

        self.seasonal_fract = seasonal_fract
        ev_growth = [ev_growth,ev_growth/2]
        pop_growth = [pop_growth,pop_growth/2]

        self.num_agents = len(OPS_data)
        self.schedule = RandomActivation(self)
        self.datacollector = DataCollector(
            model_reporters={"day": "day",
                                "hour": "hour", 
                                'EVs':'tot_EVs',
                                'total_daily_use':'total_daily_use',
                                'pop_daily_use':'pop_daily_use',
                                'ev_daily_use':'ev_daily_use'}, 
            agent_reporters={"EV_sat": "EV_sat",
                                'Pop':'Pop',
                                'EVs':'EVs',
                                'total_daily_use':'total_daily_use',
                                'pop_daily_use':'pop_daily_use',
                                'ev_daily_use':'ev_daily_use'}
        )

        model_rep_hours = dict(zip([str(x) for x in np.arange(24)],[str(x) for x in np.arange(24)]))
        self.datacollector_hours = DataCollector(
            model_reporters=model_rep_hours
        )
        self.day=0
        self.total_load_curve = pd.DataFrame()

        
        # Create agents
        for i,row in OPS_data.iterrows():
            a = OPS(i, self, row, load_curve,EV_load_base, pop_growth, ev_growth,seasonal_fract=self.seasonal_fract)
            self.schedule.add(a)

        self.running = True
        self.collect()
        self.datacollector.collect(self)
        self.datacollector_hours.collect(self)

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
        load_curve_list = []
        for agent in self.schedule.agents:
            load_curve_list.append(agent.load_curve)
            self.tot_EVs += agent.EVs
            self.total_daily_use += agent.total_daily_use
            self.pop_daily_use += agent.pop_daily_use
            self.ev_daily_use += agent.ev_daily_use
        self.load_curve = pd.concat(load_curve_list,axis=1).reset_index()
        self.load_curve['Total'] = self.load_curve.sum(axis=1)
        self.load_curve['Date'] = self.day
        

        for k,v in self.load_curve['Total'].to_dict().items():
            setattr(self,str(k),v)

    def run_model(self, n):
        for i in range(n):
            self.step()
                

