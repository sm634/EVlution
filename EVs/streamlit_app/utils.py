import altair as alt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import glob
import datetime 


def get_data():
    names = glob.glob('../Data/mdf*.csv')
    data_list = []
    for file in names:
        data = pd.read_csv(
            file,
            parse_dates=[
                "date_time"
            ],  # set as datetime instead of converting after the fact
        )
        data_list.append(data)
    data_all = pd.concat(data_list,ignore_index=True)
    return data_all

def is_business_day(date):
        return bool(len(pd.bdate_range(date,date)))

def data_subset(data_all,locs,timeframe,specific_date):
    if locs != ['All']:
        data = data_all[data_all['model_name'].isin(locs)]
    else:
        data = data_all.copy()
    data['isbusinessday'] = [is_business_day(date) for date in data.date_time]
    data['hour'] = pd.to_datetime(data.date_time).dt.hour
    if timeframe == ['hour']:
        data = data.groupby('hour').mean().reset_index()
        data['time_frame'] = data['hour']

    elif timeframe == ['day']:
        data['date'] = pd.to_datetime(data.date_time).dt.date
        data = data[data['date'] == specific_date]
        data['time_frame'] = data['hour'].copy()

    elif timeframe == ['weekday']:
        data = data[data['isbusinessday']]
        data = data.groupby('hour').mean().reset_index()
        data['time_frame'] = data['hour']
        
    elif timeframe == ['weekend']:
        data = data[~data['isbusinessday']]
        data = data.groupby('hour').mean().reset_index()
        data['time_frame'] = data['hour']

    else:
        data['time_frame'] = data['date_time']
    data = data.groupby('time_frame').mean().reset_index()
    return data

    
def get_agent_data(loc):
    names = glob.glob(f'../Data/adf_{loc}*.csv')
    data_list = []
    for file in names:
        data = pd.read_csv(file)
        data['seed'] = file.split('_')[-1][:-4]
        data_list.append(data)

    data_all = pd.concat(data_list,ignore_index=True)
    return data_all

def get_lat_long(agent_data):
    agent_data = agent_data.copy()
    new = agent_data["pos"].str.replace(')','', regex=True)
    new = new.str.replace('(','', regex=True)
    new = new.str.split(",", n = 1, expand = True)
    new = new.astype(float)

    agent_data['lat'] = new[1]/111
    agent_data['long'] = new[0]/111.321
    return agent_data

def colour_agents(agent_data):
    agent_data_2 = agent_data.copy()
    agent_data_2['loc'] = np.where(agent_data['moving'], 'Moving', agent_data['last_location'])
    return agent_data_2

def colour_agents_SS(agent_data):
    agent_data['loc'] = np.where(agent_data['moving'], np.where(agent_data['charge']<25,'black', 'blue' ), 
                                np.where(agent_data['last_location']<'home','red', 
                                 np.where(agent_data['last_location']<'work','green', 
                                  np.where(agent_data['last_location']<'charge','teal', 
                                   np.where(agent_data['last_location']<'random','pink', 'yellow' ) 
                                  )
                                 )
                                )
                            )
    return agent_data
