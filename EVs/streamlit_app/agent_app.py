
import streamlit as st
import glob
import plotly.graph_objects as go
import plotly.express as px
import operator
import functools

from utils import get_agent_data, get_lat_long, colour_agents


def gen_data(agent_data_source, seed):
    
    agent_data_source = agent_data_source[agent_data_source['seed']==seed]

    agent_data = get_lat_long(agent_data_source)
    agent_data = colour_agents(agent_data)
    # agent_data['charge'] = round(agent_data['charge'],2)
    
    # agent_step_data = agent_data.loc[(agent_data['Step']==step) & (agent_data['seed']==seed)]
    # agent_step_data = agent_step_data.loc[agent_step_data['seed']==seed]
    return agent_data


def gen_app_3():

    st.title("Agent Movement Application")
    st.write("see agents move around grid")

    col1, col2 = st.columns(2) # col2, col3, 
    filenames = glob.glob('../Data/adf_*')
    poss_locs = list(set([x.split('_')[1] for x in filenames]))
    with col1:
        # ticker = st.text_input("Choose a ticker (⬇💬👇ℹ️ ...)", value="⬇")#
        locs = [st.radio('locations',poss_locs, index=0 )][0]

    steps = 30
    agent_data_source = get_agent_data(locs[0])
    
    with col2:
        seed = st.radio('Seed',agent_data_source['seed'].unique() , index=0,)
    
    agent_data_source = get_lat_long(agent_data_source)
    xmax = agent_data_source['long'].max()
    xmin = agent_data_source['long'].min()
    x_range =(xmax-xmin)/10
    xmax += x_range
    xmin -= x_range

    ymax = agent_data_source['lat'].max()
    ymin = agent_data_source['lat'].min()
    y_range =(ymax-ymin)/10
    ymax += y_range
    ymin -= y_range
    

    agent_seed_data = gen_data(agent_data_source, seed)
    agent_seed_data['charge']+=50
    agent_seed_data = agent_seed_data[agent_seed_data['Step']<100]
    fig = px.scatter_mapbox(agent_seed_data, lat="lat", lon="long", animation_frame="Step",#size='charge',color='loc',#text ='AgentID',
                            hover_data=['AgentID','charge','loc','next_location'],
        )
    fig.update_layout(
        xaxis={'range':[xmin,xmax]},
        yaxis={'range':[ymin,ymax]},
        mapbox_style="open-street-map",
        margin=dict(l=5, r=5, t=5, b=5),
        width=800, height=800,autosize=False,
    )
    # print(agent_seed_data)
    fig["layout"].pop("updatemenus") # optional, drop animation buttons
    # fig.show()
    st.plotly_chart(fig, use_container_width=True)
