from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid,ContinuousSpace
from mesa.datacollection import DataCollector

import numpy as np
import pandas as pd


class OPS(Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model, ops_row, load_curve, EV_load_base):
        super().__init__(unique_id, model)
        self.load_curve_base = load_curve
        self.EV_load_base = EV_load_base

        for k,v in model.cfg['agent_params'].items():
            setattr(self,k,v)

        for k,v in ops_row.items():
            setattr(self,k,v)

        self.agent_collect()

    def charge_EV(self):
        pass
    
    def update_stats(self):
        self.EV_sat *= (1 + np.random.normal(self.ev_growth[0],self.ev_growth[1]))
        self.Pop *= (1 + np.random.normal(self.pop_growth[0],self.pop_growth[1]))
        self.EV_num = round(self.EV_sat * self.Pop)

    def agent_collect(self):
        #playing around with seeasonality
        # date_coeff = abs(self.model.date.week-26)/26
        # self.load_curve_base_season = self.load_curve_base * (1-self.seasonal_fract)  +  self.load_curve_base * date_coeff * self.seasonal_fract

        self.pop_load = (self.load_curve_base * self.Pop)
        self.ev_load = (self.EV_load_base * self.EV_num)
        self.load_curve = self.pop_load + self.ev_load
        self.load_curve.columns = [self.code]
        self.total_daily_use = self.load_curve.sum().iloc[0]
        self.pop_daily_use = self.pop_load.sum().iloc[0]
        self.ev_daily_use = self.ev_load.sum().iloc[0]
    
    def step(self):
        self.charge_EV()
        self.update_stats()
        self.agent_collect()