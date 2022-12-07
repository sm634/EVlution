import streamlit as st
import agent_app
import model_res_dash
import new_run  
import new_run_live  
import altair as alt
from streamlit_option_menu import option_menu
from  PIL import Image

# def my_theme():
#     return {
#         'config': {
#             'view': {
#                 'height': 300,
#                 'width': 400,
#             },
#             'mark': {
#                 'color': 'black',
#                 'fill': '#000000',
#             },
#             'axisLeft': {
#                 'labelFontSize': 30,
#             },
#         }
#     }
# # register the custom theme under a chosen name
# alt.themes.register('my_theme', my_theme)
# # enable the newly registered theme
# alt.themes.enable('my_theme')
# tab4, tab1, tab2, tab3 = st.tabs(['live run', "Model Tab", "Agent Movement Tab",'New Model Run'])
# with tab4:
#    new_run_live.gen_app()
# with tab1:
#    model_res_dash.gen_app()
# with tab2:
#    agent_app.gen_app_3()
# with tab3:
#    new_run.gen_app()
# with st.sidebar:


# alt.themes.enable("streamlit")

st.set_page_config(layout="wide")
logo = Image.open(r'branding//cap_logo.png')
col1, col2 = st.columns([0.8, 0.2])
with col1:
   choose = option_menu("Team Evlution - EV Simulation", ['Live Run', "Model Results", "Agent Movement",'New Model Run'], 
                  icons=['shuffle', 'bar-chart', 'pin-map', 'node-plus'],
                  menu_icon="app-indicator", default_index=0,orientation="horizontal",
                  styles={
                        #"container": {"padding": "5!important", "background-color": "#fafafa"},
                        "icon": {"color": "orange", "font-size": "25px"}, 
                        #"nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                        #"nav-link-selected": {"background-color": "#02ab21"},
                        }
   )
# with col2:
#    st.image(logo, width=250 )

if choose == 'Live Run':
   new_run_live.gen_app()
elif choose =="Model Results":
   model_res_dash.gen_app()
elif choose == "Agent Movement":
   agent_app.gen_app_3()
else:
   new_run.gen_app()
