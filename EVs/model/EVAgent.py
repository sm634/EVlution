from mesa import Agent
import numpy as np
import math

class EVAgent(Agent):
    """An Electric Vehical Agent with starting charge, home and work locations"""

    def __init__(self, unique_id, model):
        """ initialise agent from model params """

        super().__init__(unique_id, model)
        self.id = unique_id
        self.dx = 0
        self.dy = 0
        self.full = 0 # to make vis work (full corresponding to charge points)
        self.moving = True
        self.charge_drain = 0

        for k,v in model.cfg['agent_params']['EVs'].items():
            setattr(self,k,v)

        self.charge = np.random.uniform(0.5,1)*self.max_range

        #set up starting locations for the EV agent
        if len(self.model.POIs)>3:
            #fix later to be less hacky
            rand_locs = self.model.POIs.sample(3,weights=self.model.POIs.prob)
            self.locations = {  'home':     (rand_locs.iloc[0].x, rand_locs.iloc[0].y),
                                'work':     (rand_locs.iloc[1].x, rand_locs.iloc[1].y),
                                'random':   (rand_locs.iloc[2].x, rand_locs.iloc[2].y),
                        }
            self.model.POIs.loc[rand_locs.index,'uses'] += 1
        else:
            self.locations = {'home': (np.random.random() * self.model.width,
                                    np.random.random() * self.model.height),
                            'work': (np.random.random() * self.model.width,
                                    np.random.random() * self.model.height),
                            'random': (np.random.random() * self.model.width,
                                    np.random.random() * self.model.height),
                    }
        # get from POI data
        # the EV agent will always be travelling between locations last-next
        # todo set up random resting between locations and available to charge at home
        self.location_names = list(self.locations.keys())
        self.last_location = np.random.choice(self.location_names)
        locations_names_new = self.location_names[:]
        locations_names_new.remove(self.last_location)
        self.next_location = np.random.choice(locations_names_new)

        self.pos = self.locations[self.last_location]
        self.X = self.pos[0]
        self.Y = self.pos[1]
        
        self.agent_schedule()

    def __repr__(self) -> str:
        """ representation of agent """
        return "EV: {}".format(self.id)

    def move(self):
        """ Each step the EV will move toward its desired next location with a distance (speed), and use some charge (discharge_rate)
            if the EV is charging then it will not move. Once it reaches its destination a new destination will be chosen. """
            # find shortest path and move down it
            # move to network model only leave a node if can get to next
            # optimse route based on charging points

        self.moving = True
        # location based movement, EVs move toward a location, when they get there they get a new location
        pi = self.pos
        pf = self.locations[self.next_location]
        D, x_d, y_d = self.get_distance(pi, pf) # find distance and direction to location

        if D < self.speed: # if can reach destination this step
            # todo if at destination = True
            new_position = pf
            self.last_location = self.next_location
            self.dx, self.dy = 0, 0
            if self.last_location == 'charge':
                self.charging = True # reached charge point
            else:
                self.model.completed_trip += 1 # reached destination
                self.agent_schedule()
                
        else: 
            theta = math.atan(abs(y_d/x_d))
            self.dx = math.cos(theta) * self.speed * np.sign(x_d)
            self.dy = math.sin(theta) * self.speed * np.sign(y_d)
            new_position = (pi[0] + self.dx, pi[1] + self.dy) # move toward destination 
            
        self.charge -= self.discharge_rate # moving uses charge at rate = discharge_rate
        self.model.space.move_agent(self, new_position) # move agent
        self.pos = new_position # update postion

    def get_new_location(self):
        """ how to determine where to go next """
        if self.charging: # not move if still charging
            pass
        elif self.charge > 0.5: # if still got plenty of charge then select new location randomly
            self.location_names = list(self.locations.keys())
            locations_names_new = self.location_names[:]
            locations_names_new.remove(self.last_location)
            if 'charge' in locations_names_new:
                locations_names_new.remove('charge')
            
            if self.last_location =='random':
                if len(self.model.POIs)>3:
                    rand_locs = self.model.POIs.sample(1,weights=self.model.POIs.prob)
                    self.locations['random'] = (rand_locs.iloc[0].x, rand_locs.iloc[0].y)
                    self.model.POIs.loc[rand_locs.index,'uses'] += 1
                else:
                    self.locations['random'] = (np.random.random() * self.model.width,
                                                np.random.random() * self.model.height)
            
            self.next_location = np.random.choice(locations_names_new)
        else:  # if at destination but low on charge then find charging point
            self.find_closest_charge()
            self.next_location = 'charge'

    def get_distance(self, pi, pf):
        """ calculate distance and direction to next location """
        x_d = pf[0] - pi[0]
        y_d = pf[1] - pi[1]
        D = (x_d**2 + y_d**2)**0.5
        return D, x_d, y_d

    def find_closest_charge(self):
        """ scan all charge points to find closest one """
        # todo update preferences about which charge points are free
        # todo only look at nearest charge points
        distances = {}
        for i, (CL_name, CL_pos) in enumerate(self.model.charge_locations.items()):
            distances[CL_name], x_d, y_d = self.get_distance(self.pos, CL_pos)

        best_CL = min(distances, key=distances.get)
        self.locations['charge'] = self.model.charge_locations[best_CL]

    def check_charge(self):
        """ if made it to a charge point then charge untill battery fully charged
            Charges via the ChargeEV function in the chargePoint code """
        if self.charge >= 1:  # if fully charged then can move on to new location
            self.charge = 1
            self.charging = False
            self.get_new_location()

    def agent_schedule(self):
        """ Just got to new location. decide how long to wait and where to go next """
        self.moving = False
        if self.last_location == 'home': 
            self.wait = np.random.normal(self.home_stay,1)
        if self.last_location == 'work':
            self.wait = np.random.normal(self.work_stay,1)
        if self.last_location == 'random':
            self.wait = np.random.normal(self.rand_stay,1)
        self.wait = round(self.wait)


    def step(self):
        """ key agent step, can add functions in here for agent behaviours """
        
        # by default not moving on start of step
        self.charge_drain = 0
        if self.charging:
            self.check_charge()  # check if charging, if now full
        
        if self.charge <= 0.2: # if charge getting low, head straight to the nearest charge point
            self.get_new_location()
        
        #if still charging then continue untill full
        if self.charging:
            self.charge_drain = 1 # how fast charging = load
            pass # if still charging then dont move
        else:
            self.charge_drain = 0
            
        #if still waiting then continue to wait
        if self.wait > 0:
            self.wait -= 1
        #if not waiting then can move
        else : 
            #if not currently moving then choose new location and start moving
            if not self.moving:
                self.get_new_location()
            self.moving = True
            self.move()
