import streamlit as st
import datetime 
from utils import get_data, data_subset

def gen_app():
    source = get_data()
    # print(source)
    specific_date = source['date_time'].min() + datetime.timedelta(days=7)
    source = source[source['date_time']>specific_date]
    poss_locs = list(source['model_name'].unique())

    st.title("Model Results")
    st.write("Visualisation of model statistics")

    col1, col4 = st.columns(2) # col2, col3, 
    with col1:
        if st.checkbox('All Locations', value=True):
            locs = ['All']
        else:
            locs = [st.multiselect('locations',poss_locs, poss_locs[0] )][0]

    with col4:
        timeframe = [st.radio('timeframe', ['all', 'day','hour', 'weekday', 'weekend'], index=0,)]
        if timeframe == ['day']:
            specific_date = st.date_input('xxx', value=source['date_time'].min(), min_value=source['date_time'].min(), max_value=source['date_time'].max())

    # Original time series chart. Omitted `get_chart` for clarity
    data_charts = data_subset(source,locs,timeframe,specific_date)

    col1, col4 = st.columns(2) # col2, col3, 
    with col1:
        st.write("charge_load")
        st.line_chart(data_charts.set_index('time_frame')['charge_load'])
    with col4:
        st.write("EV Positions")
        st.line_chart(data_charts.set_index('time_frame')[['av_moving','av_home','av_work','av_random','av_CP']])

    col1, col4 = st.columns(2) # col2, col3, 
    with col1:
        st.write("Average Charge")
        st.line_chart(data_charts.set_index('time_frame')['av_charge']) 
    with col4:
        st.write("Price")
        st.line_chart(data_charts.set_index('time_frame')['price'])
   

