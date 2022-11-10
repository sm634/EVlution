from mesa import Agent
import numpy as np
import math

class GridAgent(Agent):
    """An Electric Vehical Agent with starting charge, home and work locations"""

    def __init__(self, unique_id, model, pos, radius):
        """ initialise agent from model params """
        super().__init__(unique_id, model)
        
        for k,v in model.cfg['agent_params']['Grid_Points'].items():
            setattr(self,k,v)

        self.id = unique_id
        self.pos = pos
        self.radius = radius
        self.X = pos[0]
        self.Y = pos[1]
        
    def __repr__(self) -> str:
        return "EV: " + self.id

    def count(self):
        neighbors = self.model.space.get_neighbors([self.pos],self.radius)
        self.cars_passing = len(neighbors)

    def step(self):
        """ key agent step, can add functions in here for agent behaviours """
        self.count()
