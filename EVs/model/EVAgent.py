from mesa import Agent
import numpy as np
import math
import pandas as pd
import pdb

class EVAgent(Agent):
    """An Electric Vehical Agent with starting charge, home and work locations"""

    def __init__(self, unique_id, model):
        """ initialise agent from model params """

        super().__init__(unique_id, model)
        self.id = unique_id
        self.dx = 0
        self.dy = 0
        self.full = 0 # to make vis work (full corresponding to charge points)
        self.moving = False
        self.charge_load = 0

        for k,v in model.cfg['agent_params']['EVs'].items():
            setattr(self,k,v)
        
        self.charge_pcnt = np.random.uniform(0.5,1) # % charge 
        self.charge = self.charge_pcnt * self.max_charge # kWh
        self.range = self.charge * self.efficiency_rating # max dist in km

        self.initialise_locs()

    def initialise_locs(self):
        #set up starting locations for the EV agent
        if len(self.model.POIs)>3:
            #fix later to be less hacky
            rand_locs = self.model.POIs.sample(frac=1,random_state=np.random.randint(10000)).copy()
            self.locations = {  'home':     (rand_locs.iloc[0]['poi_x_km'], rand_locs.iloc[0]['poi_y_km']),
                                'random':   (rand_locs.iloc[1]['poi_x_km'], rand_locs.iloc[1]['poi_y_km']),
                        }
            rand_locs['dx'] = rand_locs['poi_x_km']-rand_locs['poi_x_km'].iloc[0]
            rand_locs['dy'] = rand_locs['poi_y_km']-rand_locs['poi_y_km'].iloc[0]
            rand_locs['d'] = (rand_locs['dx']**2 + rand_locs['dy']**2)**0.5 / self.dist_per_step
            # idxs = list(rand_locs.index[:2])

            poss_work_locs = rand_locs[rand_locs['d']<self.max_work_d]
            if len(poss_work_locs)>1:
                work_loc = poss_work_locs.iloc[0]
                self.locations['work'] = (work_loc['poi_x_km'],work_loc['poi_y_km'])
                # idxs += list(poss_work_locs.index[0])
                
            # self.model.POIs.loc[idxs,'uses'] += 1
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
        
        self.last_location = self.choose_new_location(self.location_names)
        locations_names_new = self.location_names[:]
        locations_names_new.remove(self.last_location)
        self.next_location = self.choose_new_location(locations_names_new)

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
        # todo work out if agent can make it to location
        self.moving = True
        # location based movement, EVs move toward a location, when they get there they get a new location
        pi = self.pos
        pf = self.locations[self.next_location]
        D, x_d, y_d = self.get_distance(pi, pf) # find distance and direction to location

        if D < self.dist_per_step: # if can reach destination this step
            # todo if at destination = True
            self.dist_moved = D
            new_position = pf
            self.last_location = self.next_location
            self.dx, self.dy = 0, 0
            self.moving = False # stop moving
            if self.last_location == 'charge':
                self.charging = True # reached charge point
            else:
                self.model.completed_trip += 1 # reached destination
                self.completed_trip += 1
                self.agent_schedule()
        else: 
            self.dist_moved = self.dist_per_step
            theta = math.atan(abs(y_d/x_d))
            self.dx = math.cos(theta) * self.dist_per_step * np.sign(x_d)
            self.dy = math.sin(theta) * self.dist_per_step * np.sign(y_d)
            new_position = (pi[0] + self.dx, pi[1] + self.dy) # move toward destination 
            
        self.charge -= self.dist_moved / self.efficiency_rating # moving uses charge at rate = discharge_rate  # change to distance travelled
        self.model.space.move_agent(self, new_position) # move agent
        self.pos = new_position # update postion

    def get_new_location(self):
        """ how to determine where to go next """
        # if self.charging: # not move if still charging
        #     pass
        if self.charge_pcnt > self.next_point_charge: # if still got plenty of charge then select new location
            locations_names_new = self.update_possible_locations()
            self.next_location = self.choose_new_location(locations_names_new) 
        else:  # if at destination but low on charge then next stop will be to find charging point
            self.find_closest_charge()
    
    def choose_new_location(self,locations_names_new):
        loc_probs = np.array([self.model.loc_probs_hour[x] for x in locations_names_new])
        self.next_location = np.random.choice(locations_names_new, p=loc_probs/sum(loc_probs))
        return self.next_location
    
    def update_possible_locations(self):
        # cant choose last location or charging point
        self.location_names = list(self.locations.keys())
        locations_names_new = self.location_names[:]
        locations_names_new.remove(self.last_location)
        if 'charge' in locations_names_new:
            locations_names_new.remove('charge')

        # update random location if just been to one, cant be same as before, choose new POI
        if self.last_location =='random':
            if len(self.model.POIs)>3:
                rand_locs = self.model.POIs.sample(1,weights=self.model.POIs['poi_area'],random_state=np.random.randint(10000))
                self.locations['random'] = (rand_locs.iloc[0]['poi_x_km'], rand_locs.iloc[0]['poi_y_km'])
                self.model.POIs.loc[rand_locs.index,'uses'] += 1
            else:
                self.locations['random'] = (np.random.random() * self.model.width,
                                            np.random.random() * self.model.height)
        return locations_names_new


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
        self.next_location = 'charge'

    def agent_schedule(self):
        """ Just got to new location. decide how long to wait and where to go next """
        if self.last_location == 'home': 
            self.wait = np.random.normal(self.home_stay[self.model.business_day],1)
        if self.last_location == 'work':
            self.wait = np.random.normal(self.work_stay[self.model.business_day],1)
        if self.last_location == 'random':
            self.wait = np.random.normal(self.rand_stay[self.model.business_day],1)
        self.wait = round(self.wait)

    def price_function(self):
        charge_need = 1 - self.charge_pcnt
        choice_charge = True if charge_need > self.model.price else False
        return choice_charge

    def step(self):
        """ key agent step, can add functions in here for agent behaviours """
        
        self.decide_to_charge()

        if self.wait > 0:  #if still waiting then continue to wait
            self.wait -= 1
        else:  #if not waiting then can move
            if not self.moving:         # if not currently moving then choose new location and start moving
                self.get_new_location()
            elif self.charge_pcnt <= self.go_to_charge_pcnt:    # if charge getting low, head straight to the nearest charge point
                self.find_closest_charge()
            self.moving = True
            self.charging = False
            self.move()
    
    def check_charge(self):
        """ if made it to a charge point then charge untill battery fully charged
            Charges via the ChargeEV function in the chargePoint code """
        if self.charge >= self.max_charge:  # if fully charged then can move on to new location
            self.charge = self.max_charge
            self.charging = False
            self.wait = 0  # can now move this step
        else: 
            self.wait = 1  # will not move this step
            self.charging = True
            
    def decide_to_charge(self):
        self.dist_moved = 0
        self.charge_load = 0 
        self.range = self.charge * self.efficiency_rating
        self.charge_pcnt = self.charge / self.max_charge

        #if at home, work or charging point then could be charging. decide on if want to via price
        if self.moving:
            return 
        if self.charge_pcnt >= 1:
            self.charge = self.max_charge
            self.charge_pcnt = 1 
            self.charging = False
            return 
 
        if self.last_location == 'home' and self.home_charge_rate != 0:
            if self.price_function():
                self.charging = True
                self.charge_load = self.home_charge_rate  # slow charge
        elif self.last_location == 'work' and self.work_charge_rate != 0 :
            if self.price_function():
                self.charging = True
                self.charge_load = self.work_charge_rate  # slow charge
        # if at charging point and not moving then charge from point and check if full
        elif self.last_location == 'charge':
            self.check_charge()
            if self.charging:
                self.charge_load = self.ChargePoint_charge_rate  # fast charge, set via charge point attr
                
        charge_req = self.max_charge - self.charge
        self.charge_load = min(self.charge_load,charge_req)
        self.charge += self.charge_load
