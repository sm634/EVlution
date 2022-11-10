from mesa import Agent
import numpy as np
import math

class GridAgent(Agent):
    """An Electric Vehical Agent with starting charge, home and work locations"""

    def __init__(self, unique_id, model, pos, radius):
        """ initialise agent from model params """
        super().__init__(unique_id, model)
        self.id = unique_id
        self.pos = pos
        self.X = pos[0]
        self.Y = pos[1]
        self.radius = radius
        self.cars_passing = 0
        self.Type = 'GP'
        
    def __repr__(self) -> str:
        return "EV: " + self.id

    def count(self):
        neighbors = self.model.space.get_neighbors([self.pos],self.radius)
        self.cars_passing = len(neighbors)

    def step(self):
        """ key agent step, can add functions in here for agent behaviours """
        self.count()
