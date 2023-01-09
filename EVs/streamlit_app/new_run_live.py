
import streamlit as st
import glob
import os
from utils import  data_subset, data_plot
import pandas as pd
import time
import asyncio
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

mapboxt = "pk.eyJ1IjoiZ3doYXJmIiwiYSI6ImNsYjNneW1iODA4b3kzcG10aW1qdzg0ZmcifQ.Dr044RJYsfRVTs-tp00dMA" ## open(".mapbox_token").read().rstrip() #my mapbox_access_token 
# px.set_mapbox_access_token(mapboxt)

lat_corr = 111.0
long_corr = 111.32

def setup_model(**kwargs):
    print('set up model')
    os.chdir('../')
    from model.model import EVSpaceModel
    st.session_state.model = EVSpaceModel(**kwargs)  
    os.chdir('streamlit_app')
    # return model

async def run_live_model( per_second):
    while True:
        # model.run_model(kwargs['run_len'])
       
        print(time.time())
        st.experimental_rerun()
        # return model

def portrayal_method(agent): 
    portrayal = {"Shape": "circle", "Filled": "true", "r": 2}
    x, y = agent.pos
    portrayal["long"] = x/long_corr
    portrayal["lat"] = y/lat_corr
    portrayal['AgentID'] = agent.unique_id
    if agent.Type == 'CP':
        portrayal['charge'] = 0
        portrayal['next_location'] = 0
        portrayal['symbol']= 'square'
        portrayal['loc'] = 'Charging Point'
        portrayal['r'] = 10
        
        if agent.full:
            portrayal["Color"] = "red"
        else:
            portrayal["Color"] = "Black"
    else:
        portrayal["r"] = 2
        portrayal['symbol']= 'bus'
        portrayal["loc"] = 'moving' if agent.moving else agent.last_location
        if agent.large_id:
            portrayal["Layer"] = 5
            portrayal["r"] = 10

    return portrayal

def plot_model():
    # df = px.data.iris()
    # fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")
    # st.plotly_chart(fig, use_container_width=True)
    # return fig

    space_state = [] 
    for schedule_name in st.session_state.model.schedule_list:
        agent_list = getattr(st.session_state.model,schedule_name).agents
        for idx, obj in enumerate(agent_list):
            portrayal = portrayal_method(obj)
            
            space_state.append(portrayal)
    agent_data = pd.DataFrame(space_state)
    loc_list = agent_data['loc'].unique()
    loc_list.sort()
    print(loc_list) 

    ####### Normal Scatter Mapbox
    fig = go.Figure(px.scatter_mapbox(agent_data, lat="lat", lon="long", color='loc',category_orders={'loc': loc_list}))
    # fig = go.Figure(go.Scattermapbox(mode = "markers", lat=agent_data["lat"], lon=agent_data["long"], marker =go.scattermapbox.Marker( {'symbol':'bus'})))#, color='loc',category_orders={'loc': loc_list})
    
    fig.update_layout(  xaxis={'range':[st.session_state.model.xmin/long_corr,    st.session_state.model.xmax/long_corr]},
                        yaxis={'range':[st.session_state.model.ymin/lat_corr,st.session_state.model.ymax/lat_corr]},
                        mapbox_style="open-street-map",
                        margin=dict(l=0, r=0, t=0, b=0),
                    )

    st.write(f"date {st.session_state.model.date_time.strftime('%Y-%m-%d')} hour {st.session_state.model.date_time.strftime('%H')}")
    st.plotly_chart(fig, use_container_width=True)


    mdf = st.session_state.model.datacollector.get_model_vars_dataframe()
    mdf['hour'] = pd.to_datetime(mdf.date_time).dt.hour
    mdf = mdf.set_index('date_time')
    
    col1, col4, col5 = st.columns(3) # col2, col3, 
    with col1:
        st.write("Charge Load Overall")
        st.line_chart(mdf['charge_load'])
    with col4:
        st.write("Charge Load per Hour")
        st.line_chart(mdf.groupby('hour').mean()['charge_load']*100)
    with col5:
        st.write("EVs Positions %")
        st.line_chart(mdf[['av_moving','av_home','av_work','av_random','av_CP']]*100)



    return fig


def gen_app():
    filenames = glob.glob('../configs/*.yml')
    poss_cfg = list(set([x.split('/')[1] for x in filenames]))
    with st.sidebar:
        st.write("Give Model name and parameters")
        st.write("if model data already exists then can  examine results if not will gen new model run")
        # col1, col2= st.columns(2) # col2, col3
        # with col1:
        model_name = st.text_input('Model Name', value="NewRun")
        seed = st.slider('seed2', 0, 100,1)
        # with col2:
        cfg = st.radio('Configuration',poss_cfg, index=4 )

        col1, col3 = st.columns(2) # col2, col3
        with col1:
            dist_per_step = st.slider('Dist per Step km', 1, 30,20)
        with col3:
            price_peak = st.slider('Peak', 0, 20,15)

        col2, col3 = st.columns(2) # col2, col3
        with col2:
            price_off_peak = st.slider('Off Peak Price', 0, 20,7)
        with col3:
            price_mid_peak = st.slider('Mid Peak Price', 0, 20,10)
            
        col1, col3 = st.columns(2) # col2, col3
        hours = set(np.arange(24))
        with col1:
            winter_peaks = st.multiselect('Winter Peak Hours',list(hours), [7,8,9,10,17,18] )
            print(winter_peaks)
        with col3:
            winter_mid_peaks =  st.multiselect('Winter Mid Hours',list(hours-set(winter_peaks)), [11,12,13,14,15,16] )
    
    kwargs = dict(cfg=cfg, ModelP_model_name = model_name, 
                    ModelP_seed = seed, EVP_dist_per_step = dist_per_step,
                    ModelP_price_peak = price_peak, ModelP_price_off_peak = price_off_peak, ModelP_price_mid_peak = price_mid_peak,
                    ModelP_winter_peaks = winter_peaks, ModelP_winter_mid_peaks = winter_mid_peaks )
    model_running = False
    specific_date = []
    mdf = []
    file_name = f'../Data/mdf_{model_name}_{seed}.csv'
    st.session_state['key'] = 'value'

    st.title(f"Name: {model_name} and Seed: {seed}")
    if len(glob.glob(file_name))>0:
        st.title(f"Model Already Exists")
        st.write(f"See Below the charts for that model run")

        mdf = pd.read_csv(file_name,
            parse_dates=[
                "date_time"
            ],  # set as datetime instead of converting after the fact
        )
        
        timeframeXX = [st.radio('timeframeXX2', ['all', 'day','hour', 'weekday', 'weekend'], index=0,)]
        if timeframeXX == ['day']:
            specific_date = st.date_input('xxx2', value=mdf['date_time'].min(), min_value=mdf['date_time'].min(), max_value=mdf['date_time'].max())
        # with col_aa:
        #     cc = st.text_input('ccc', value="NewRun")

        # Original time series chart. Omitted `get_chart` for clarity
        data = data_subset(mdf,[model_name],timeframeXX,specific_date)
        col1, col4 = st.columns(2) # col2, col3, 
        with col1:
            st.write("charge_load")
            st.line_chart(data_plot(data, ['charge_load']))
        with col4:
            st.write("EVs Positions %")
            st.line_chart(data_plot(data, ['av_moving','av_home','av_work','av_random','av_CP'])*100)

        col1, col4 = st.columns(2) # col2, col3, 
        with col1:
            st.write("Average Charge")
            st.line_chart(data_plot(data, ['av_charge'])) 
        with col4:
            st.write("Price")
            st.line_chart(data_plot(data, ['price']))
    else:
        st.title(f"Generate New Run")
        st.write(f"Once Happy with parameters above then click the button below to run a new model run")
        col1, col2, col3, col4 = st.columns(4) # col2, col3,
        with col1:
            st.session_state.start = st.button('Start')
        with col2:
            st.session_state.stop = st.button('Stop')
        with col3:
            st.session_state.reset = st.button('Reset', on_click=setup_model,kwargs=kwargs)
        with col4:
            steps_second = st.slider('Steps Per Second', 1, 20,5)
        
        if 'model' not in st.session_state:
            st.session_state.steps = 0
            setup_model(**kwargs)       
            st.session_state.running = False            
        
        if st.session_state.reset:
            st.session_state.running = False
            st.session_state.steps = 0
            print('reset')
            plot_model()
            
        if st.session_state.start:
            st.session_state.running = True
            print('start')
            # st.write("Started process with pid:", state.pid)
        if st.session_state.stop:
            print('stop')
            st.session_state.running = False
            plot_model()
        
        while st.session_state.running:
            st.session_state.model.step()
            st.session_state.steps +=1 
            print(st.session_state.steps)
            
            plot_model()
            time.sleep(1/steps_second)

            st.experimental_rerun()