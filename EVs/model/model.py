from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid, ContinuousSpace
from .EVAgent import EVAgent
from .ChargePoint import ChargePoint
from .GridAgent import GridAgent
import numpy as np
import pandas as pd
import itertools
import yaml
from .datacollection import DataCollector
import datetime
import collections.abc


class EVSpaceModel(Model):
    """ Electric Vehical Model, where cars drive around between locations then pull into charge points """

    def __init__(self, **kwargs):
        """ initalisation of the model, set up agent space, agents and collection modules"""

        # Read in configuration files from yaml. If any additional configs then will overwrite base

        self.read_configs(kwargs)

        if self.seed == 'None':
            self.seed = np.random.randint(10000)

        self.random.seed(self.seed)
        np.random.seed(self.seed)
        self.location_probs_weekday = pd.read_csv(self.location_probs_weekday).set_index('hour')
        self.location_probs_weekend = pd.read_csv(self.location_probs_weekend).set_index('hour')
        self.date_time = pd.to_datetime(self.start_date)
        self.business_day = 1
        self.peak_times = []
        self.mid_peak_times = []
        self.evpopratio = self.rep_agents/self.total_agents

        self.get_loc_probs()
        self.get_peak_times()
        self.set_price()
        self.completed_trip = 0

        # Set up points of interest that the agents will choose from
        # this also defines the parameter space for locations where an agent can be
        # then also pick and save the lat/lon for use in vis
        if self.POI_file != 'None':
            self.POIs = pd.read_csv(self.POI_file).set_index('poi_name')
            self.POIs['uses'] = 0
            self.xmin = min(self.POIs['poi_x_km']) - self.tol
            self.xmax = max(self.POIs['poi_x_km']) + self.tol
            self.ymin = min(self.POIs['poi_y_km']) - self.tol
            self.ymax = max(self.POIs['poi_y_km']) + self.tol
            self.width = self.xmax - self.xmin
            self.height = self.ymax - self.ymin

            x = (max(self.POIs['poi_x']) + min(self.POIs['poi_x'])) / 2
            y = (max(self.POIs['poi_y']) + min(self.POIs['poi_y'])) / 2
            self.COM = (x, y)
            self.lon = x
            self.lat = y
        else:
            self.POIs = []
            self.xmin, self.ymin = -self.tol, -self.tol
            self.xmax, self.ymax = self.width, self.height
            self.lon = self.xmin + self.width / 2
            self.lat = self.ymin + self.height / 2
            self.COM = (self.lon, self.lat)

        # set up model space
        self.space = ContinuousSpace(self.xmax, self.ymax, False,
                                     x_min=self.xmin, y_min=self.ymin)
        # set up EV agents
        self.schedule = RandomActivation(self)
        self.schedule_list = ['schedule']
        self.datacollector = DataCollector(schedule='schedule',
                                           model_reporters=self.cfg['output']['model_reporters'],
                                           agent_reporters=self.cfg['output']['agent_reporters']
                                           )
        for i in range(self.cfg['agent_params']['EVs']['num_agents']):
            a = EVAgent(i, self)
            self.schedule.add(a)
            # Add the agent to a random space
            self.space.place_agent(a, a.pos)

        # set up charging points
        self.schedule_CP = RandomActivation(self)
        self.schedule_list.append('schedule_CP')
        self.datacollector_CP = DataCollector(schedule='schedule_CP',
                                              agent_reporters={"cars_charging": "cars_charging",
                                                               'full': 'full'}
                                              )
        self.gen_CPs()

        # set up grid points for analysis
        self.schedule_gridpoints = RandomActivation(self)
        # self.schedule_list.append('schedule_gridpoints')
        self.datacollector_gridpoints = DataCollector(schedule='schedule_gridpoints',
                                                      agent_reporters={'pos': 'pos',
                                                                       "cars_passing": "cars_passing",
                                                                       'X': 'X', 'Y': 'Y'}
                                                      )
        self.gen_GPs()
        self.schedule_gridpoints.step()

        # collect starting values of all the observables, eg av charge of agents etc and update ready for collection
        self.update_vars()
        # collect from each schedule, this adds to the back end where can then pull through tables to show what happened each step
        # .collect() functions read from agent/model reporters as defined above to grab all the observables from the agents in schedules and overall model class
        self.datacollector.collect(self)
        self.datacollector_CP.collect(self)
        self.datacollector_gridpoints.collect(self)
        self.running = True

    def update(self, d, u):
        """ function to update multi level dictionary whilst preserving all emelents of dict
            this is vital for use updating the configurations """
        for k, v in u.items():
            if isinstance(v, collections.abc.Mapping):
                d[k] = self.update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    def read_configs(self, kwargs):
        """ Read in configuation parameters from file given to set up model and agents"""

        # read in base config to update all params in there first
        cfg_file = 'configs/base_cfg.yml'
        with open(cfg_file, 'r') as ymlfile:
            self.cfg = yaml.safe_load(ymlfile)
            # if additional config file given then overwrite all vals in the new config over the base configs
            # note new config will just overwrite what is there
        if 'cfg' in kwargs.keys():
            if kwargs['cfg'] != 'None':
                cfg_file = kwargs['cfg']
                with open(cfg_file, 'r') as ymlfile:
                    cfg_updates = yaml.safe_load(ymlfile)
                self.cfg = self.update(self.cfg, cfg_updates)
                # self.cfg.update(cfg_updates)

        # loops through user set params and overwrites congif in particular areas
        # any additional key word arguments given in modle run instance will overwrite any params from the config file.
        # this is how we can use the vis tool to update params
        for key, val in kwargs.items():
            if 'ModelP_' in key and val != 'base':
                key_new = key.replace("ModelP_", "")
                self.cfg['model_params'][key_new] = val
            elif 'EVP_' in key and val != 'base':
                key_new = key.replace("EVP_", "")
                self.cfg['agent_params']['EVs'][key_new] = val
            elif 'ChargeP_' in key and val != 'base':
                key_new = key.replace("ChargeP_", "")
                self.cfg['agent_params']['Charge_Points'][key_new] = val

        # take model_params from config file and assign them as attributes to model class
        for k, v in self.cfg['model_params'].items():
            setattr(self, k, v)
        # print(self.cfg)

    def gen_CPs(self):
        ''' determine charge point locations, either uniform or randomly distribute '''
        self.CP_loc = self.cfg['agent_params']['Charge_Points']['CP_loc']
        self.N_Charge = self.cfg['agent_params']['Charge_Points']['N_Charge']
        if isinstance(self.CP_loc, pd.DataFrame):
            self.N_Charge = len(self.CP_loc)
            names = self.CP_loc.index
            x_pos = self.CP_loc['x_km'].values
            y_pos = self.CP_loc['y_km'].values
        elif '.csv' in self.CP_loc:
            self.CP_locs = pd.read_csv(self.CP_loc).set_index('Station_Name')
            self.N_Charge = len(self.CP_locs)
            names = self.CP_locs.index
            x_pos = self.CP_locs['x_km'].values
            y_pos = self.CP_locs['y_km'].values
        elif self.CP_loc == 'uniform':
            indices = np.arange(0, self.N_Charge, dtype=float) + 0.5
            r = np.sqrt(indices / self.N_Charge)
            theta = np.pi * (1 + 5 ** 0.5) * indices
            x_pos = r * np.cos(theta) * self.width / 2 + self.width / 2 + self.xmin
            y_pos = r * np.sin(theta) * self.height / 2 + self.height / 2 + self.ymin
        else:
            x_pos = np.random.random(self.N_Charge) * self.width + self.xmin
            y_pos = np.random.random(self.N_Charge) * self.height + self.ymin

        charge_locs = list(zip(x_pos, y_pos))
        # print(charge_locs)

        # create and place charge points
        self.charge_locations = {}
        for i in range(self.N_Charge):
            name = str(i) + '_Charge'

            pos = charge_locs[i]
            try:
                a = ChargePoint(name, self, pos)
                self.schedule_CP.add(a)

                # Add the agent to space
                self.space.place_agent(a, pos)
                self.charge_locations[name] = pos
            except:
                print(f'Charge Point Failed {name} {pos}')

    def gen_GPs(self):
        ''' determine grid point locations, to collect traffic from EVs passing '''
        grid_spacing = self.cfg['agent_params']['Grid_Points']['grid_spacing']
        if type(grid_spacing) == int:
            grid_locs_x = np.linspace(self.xmin + self.tol, self.xmax - self.tol, grid_spacing)
            grid_locs_y = np.linspace(self.ymin + self.tol, self.ymax - self.tol, grid_spacing)
            grid_locs = itertools.product(grid_locs_x, grid_locs_y)
            radius = (self.width + self.height) / (2 * grid_spacing)
            for i, pos in enumerate(grid_locs):
                a = GridAgent(i, self, pos, radius)
                self.schedule_gridpoints.add(a)
                # Add the agent to a random space
                self.space.place_agent(a, a.pos)

    def is_business_day(self, date):
        """ calculates if the current day is a business day (not weekend or holiday) """
        self.business_day = bool(len(pd.bdate_range(date, date)))

    def get_loc_probs(self):
        """ uses business day logic to find locations of next location probabilites for agents """

        self.is_business_day(self.date_time)

        if self.business_day:
            self.loc_probs_hour = self.location_probs_weekday.loc[self.date_time.hour].to_dict()
            # could add something here to check if peak time leads to peak price
            self.get_peak_times()
        else:
            self.loc_probs_hour = self.location_probs_weekend.loc[self.date_time.hour].to_dict()
            self.peak_time = 'off'
            # this will always be off peak time

        self.set_price()

    def set_price(self):
        """ simple price mechanism which checks the price data frame and the hour associated """
        if self.date_time.hour in self.peak_times:
            self.price = self.price_peak
        elif self.date_time.hour in self.mid_peak_times:
            self.price = self.price_mid_peak
        else:
            self.price = self.price_off_peak

    def get_peak_times(self):
        """ work out what peak time it is, on off or mid, which affects price """
        if self.price_set_mechanism != 0:
            if self.date_time.month in [11, 12, 1, 2, 3, 4]:
                self.season = 'Winter'
                if self.business_day:
                    self.peak_times = self.winter_peaks
                    self.mid_peak_times = self.winter_mid_peaks
                else:
                    self.peak_times = []
                    self.mid_peak_times = []
            else:
                self.season = 'Summer'
                if self.business_day:
                    self.peak_times = self.summer_peaks
                    self.mid_peak_times = self.summer_mid_peaks
                else:
                    self.peak_times = []
                    self.mid_peak_times = []

    def update_rep_agents(self):
        #Careful of rounding, the calculation only seems ineffecient because care has to be taken not to round down
        self.agent_change = self.total_agents*self.growth_rate
        self.total_agents = self.total_agents + self.agent_change
        self.rep_agents = round(self.evpopratio*self.total_agents)

    def step(self):
        """ This is the key model function which is run once each step. Here we loop through the agent schedule,
        which performs each agent step """
        self.date_time += datetime.timedelta(hours=self.time_increment)
        self.get_loc_probs()
        self.get_peak_times()
        self.set_price()
        self.update_rep_agents()
        self.completed_trip = 0
        # call step function for every agent in each schedule
        self.schedule.step()  # EV agent step()
        self.schedule_CP.step()  # charge point agent step()
        self.schedule_gridpoints.step()  # gridpoint agent step()
        self.collect()  # collect all the data from the completed step to update model and agent dataframes

    def update_vars(self):
        """ function to iupdate observables in the model to represent all EVs in the model """
        charge_list = []
        charge_load = []
        locs = []
        # crudely loop through each agent and grab their stats
        for agent in self.schedule.agents:
            charge_list.append(agent.charge)
            charge_load.append(agent.charge_load)
            if agent.moving:
                locs.append('moving')
            else:
                locs.append(agent.last_location)

        charge_list = np.array(charge_list)
        locs = np.array(locs)

        # assign model stats to be collected by model_reporters in datacollection
        self.av_charge = np.mean(charge_list)
        self.charge_load = sum(charge_load)
        self.dead_cars = len(charge_list[charge_list < 0]) / len(charge_list)
        self.av_moving = np.mean(locs == 'moving')
        self.av_home = np.mean(locs == 'home')
        self.av_work = np.mean(locs == 'work')
        self.av_random = np.mean(locs == 'random')
        self.av_CP = np.mean(locs == 'charge')

    def collect(self):
        ''' collect data from agents and model and save to datacollection objects '''
        self.update_vars()
        self.datacollector.collect(self)  # collect agent and model information
        self.datacollector_CP.collect(self)  # collect agent and model information
        self.datacollector_gridpoints.collect(self)  # collect agent and model information

        # to actually save the results need to use save() functions

    def run_model(self, n):
        """ if running offline model then can use this to run full model span """
        for i in range(n):
            self.step()

    def save(self):
        """ save out model/agent dataframes if given model name """
        # add new funct similar to this but save to online storeage

        if self.model_name != 0:
            mdf = self.datacollector.get_model_vars_dataframe()

            # checks to see in the config if the user wants to save model dataframes and agent data frames for Evs,
            # charge points and grid points
            if self.cfg['output']['save_data']['model']:
                mdf.to_csv('Data/mdf_{}_{}.csv'.format(self.model_name, self.seed))

            if self.cfg['output']['save_data']['EVs']:
                adf = self.datacollector.get_agent_vars_dataframe()
                adf.to_csv('Data/adf_{}_{}.csv'.format(self.model_name, self.seed))

            if self.cfg['output']['save_data']['CPs']:
                adf = self.datacollector_CP.get_agent_vars_dataframe()
                adf.to_csv('Data/adf_CP_{}_{}.csv'.format(self.model_name, self.seed))

            if self.cfg['output']['save_data']['GPs']:
                adf = self.datacollector_gridpoints.get_agent_vars_dataframe()
                adf.to_csv('Data/adf_GP_{}_{}.csv'.format(self.model_name, self.seed))
