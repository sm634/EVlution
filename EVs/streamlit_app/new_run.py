
import streamlit as st
import glob
import os
from utils import  data_subset, data_plot
import pandas as pd

def run_new_model(**kwargs):
    os.chdir('../')
    from model.model import EVSpaceModel
    model = EVSpaceModel(**kwargs)  
    model.run_model(kwargs['run_len'])
    model.save()
    os.chdir('streamlit_app')


def gen_app():
    st.title("Generate New Run")
    st.write("Give Model name and parameters")
    st.write("if model data already exists then can  examine results if not will gen new model run")


    filenames = glob.glob('../configs/*.yml')
    poss_cfg = list(set([x.split('/')[1] for x in filenames]))
    
    col1, col2= st.columns(2) # col2, col3
    with col1:
        model_name = st.text_input('Model Name', value="NewRun")
    with col2:
        cfg = [st.radio('Configuration',poss_cfg, index=0 )][0]

    col1, col2, col3 = st.columns(3) # col2, col3
    with col1:
        dist_per_step = st.slider('Dist per Step km', 1, 30,20)
    with col2:
        seed = st.slider('seed', 0, 100,1)
    with col3:
        run_len = st.slider('run_len', 0, 500,240)
    
    
    kwargs = dict(cfg=cfg, run_len = run_len, ModelP_model_name = model_name, ModelP_seed = seed,EVP_dist_per_step = dist_per_step)
    model_running = False
    specific_date = []
    mdf = []
    file_name = f'../Data/mdf_{model_name}_{seed}.csv'
    
    st.title(f"Name: {model_name} and Seed: {seed}")
    if len(glob.glob(file_name))>0:
        st.title(f"Model Already Exists")
        st.write(f"See Below the charts for that model run")

        mdf = pd.read_csv(file_name,
            parse_dates=[
                "date_time"
            ],  # set as datetime instead of converting after the fact
        )
        
        timeframeXX = [st.radio('timeframeXX', ['all', 'day','hour', 'weekday', 'weekend'], index=0,)]
        if timeframeXX == ['day']:
            specific_date = st.date_input('xxx', value=mdf['date_time'].min(), min_value=mdf['date_time'].min(), max_value=mdf['date_time'].max())
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
        st.title(f"Model Version does not Exist")
        st.write(f"Once Happy with parameters above then click the button below to run a new model run")
        with st.spinner("Running Model"):
            run_model = st.button('Run New Model', on_click=run_new_model,kwargs=kwargs)
        

