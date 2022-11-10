from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid,ContinuousSpace
from mesa.datacollection import DataCollector

import numpy as np
from numpy import pi, cos, sin, sqrt, arange
import matplotlib.pyplot as pp

class ChargePoint(Agent):
    """A Charging point agent where EVs come to charge back up """

    def __init__(self, unique_id, model, pos):
        """ Set up charge point with locations etc """
        super().__init__(unique_id, model)
        
        for k,v in model.cfg['agent_params']['Charge_Points'].items():
            setattr(self,k,v)
            
        self.pos = pos
        self.X = self.pos[0]
        self.Y = self.pos[1]

    def ChargeEV(self):
        """ count number of cars charging """
        cellmates = self.model.space.get_neighbors([self.pos],0)
        self.cars_charging = 0 
        for EV in cellmates:
            if EV.Type == 'EV' and EV.charging:
                self.cars_charging += 1
                EV.charge += self.charge_rate 

    def step(self):
        """ Charge point step behaviour """
        self.ChargeEV()
        self.full = True if self.cars_charging >= self.CP_capacity else False