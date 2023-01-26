import streamlit as st
import datetime 
from utils import get_data, data_subset, data_plot


def data_plot(data, fields, together):
    if together:
        data_charts = data.groupby('time_frame').mean()[fields]
    else:
        data_charts = data.groupby(['time_frame','model_name']).mean()[fields].unstack()
        data_charts.columns = data_charts.columns.get_level_values(1)

    return data_charts

def gen_app():
    source = get_data()
    # print(source)
    specific_date = source['date_time'].min() + datetime.timedelta(days=7)
    source = source[source['date_time']>specific_date]
    poss_locs = list(source['model_name'].unique())

    st.title("Model Results")
    st.write("Visualisation of model statistics")
    # with st.sidebar:
    col1, col2, col4 = st.columns(3) # col3, 
    with col1:
        if st.checkbox('All Locations', value=True):
            locs = ['All']
        else:
            locs = [st.multiselect('locations',poss_locs, poss_locs[0] )][0]
    with col2:
        together = st.radio('Together',[True, False],index=0)
    with col4:
        timeframe = [st.radio('timeframe', ['all', 'day','hour', 'weekday', 'weekend'], index=0,)]
        if timeframe == ['day']:
            specific_date = st.date_input('xxx', value=source['date_time'].min(), min_value=source['date_time'].min(), max_value=source['date_time'].max())

    # Original time series chart. Omitted `get_chart` for clarity
    data = data_subset(source,locs,timeframe,specific_date)
    col1, col4 = st.columns(2) # col2, col3, 
    with col1:
        st.write("Charge Load per Agent")
        data['charge_load_rep'] = data['charge_load'] / data['rep_agents']
        st.line_chart(data_plot(data, ['charge_load_rep'], together))
    with col4:
        if not together: 
            st.write("EVs Moving %")
            st.line_chart(data_plot(data, ['av_moving'], together)*100)
        else:
            st.write("EVs Positions %")
            st.line_chart(data_plot(data, ['av_moving','av_home','av_work','av_random','av_CP'], together)*100)

    col1, col4 = st.columns(2) # col2, col3, 
    with col1:
        st.write("Number of representative agents")
        st.line_chart(data_plot(data, ['rep_agents'], together)) 
    with col4:
        st.write("Price of Charging for Agents")
        st.line_chart(data_plot(data, ['price'], together))
   

