import altair as alt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import glob
import datetime 

@st.cache
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
    data_all['charge_load'] *= data_all['rep_agents']/1000
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
        data['time_frame'] = data['hour']

    elif timeframe == ['day']:
        data['date'] = pd.to_datetime(data.date_time).dt.date
        data = data[data['date'] == specific_date]
        data['time_frame'] = data['hour'].copy()

    elif timeframe == ['weekday']:
        data = data[data['isbusinessday']]
        data['time_frame'] = data['hour']
        
    elif timeframe == ['weekend']:
        data = data[~data['isbusinessday']]
        data['time_frame'] = data['hour']

    else:
        data['time_frame'] = data['date_time']
    
    return data

def data_plot(data, fields, together = True):
    if together:
        data_charts = data.groupby('time_frame').mean()[fields]
    else:
        data_charts = data.groupby(['time_frame','model_name']).mean()[fields].unstack()
        data_charts.columns = data_charts.columns.get_level_values(1)

    return data_charts

@st.cache 
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



#####
    ######## Symbol mapbox
    
    # fig = go.Figure(go.Scattermapbox(mode = "markers", lat=agent_data["lat"], lon=agent_data["long"], marker =go.scattermapbox.Marker( {'size' : agent_data['r'],'symbol': agent_data['symbol']})),)
    #             size='charge',text ='AgentID',#hover_data=['AgentID','charge','loc','next_location'],)
    

#     scatt = go.Scattermapbox( lat=agent_data["lat"], lon=agent_data["long"], mode = "markers",)#marker=dict(symbol ='marker', size=15, color='blue'))
#     layout = go.Layout(title_text ='Pin location at a few cities in Netherlands', 
#                    title_x =0.5, width=750, height=700,
#                 #    mapbox_style="open-street-map",
#                     mapbox_accesstoken= mapboxt,
#                     mapbox_style = "mapbox://styles/gwharf/clb3hfgeo000314o88dkwagt8",
#                     # mapbox = dict(center= dict(lat=agent_data["lat"].mean(), lon=agent_data["long"].mean()),            
#                     #                 zoom=6,
#                     #                 # style="light",
#                     #                 style="open-street-map",),
#                             )
                            
#     fig=go.Figure(data=[ scatt], layout =layout)

#     fig.add_trace(
#         go.Scattermapbox(
#             mode="markers+lines",
#             lon=[-50, -60, 40],
#             lat=[30, 10, -20],
#             marker={"size": 10, "symbol": "circle"},
#         )
#     )
#     fig.update_layout(
#     margin={"l": 0, "t": 0, "b": 0, "r": 0},
#     mapbox={
#         "center": {"lon": 10, "lat": 10},
#         "style": "stamen-terrain",
#         "center": {"lon": -20, "lat": -20},
#         "zoom": 1,
#     },
# )