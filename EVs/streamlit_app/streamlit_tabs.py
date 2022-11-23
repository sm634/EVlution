import streamlit as st
import agent_app
import model_res_dash
import new_run  
import altair as alt


st.set_page_config(layout="wide")
tab1, tab2, tab3 = st.tabs(["Model Tab", "Agent Movement Tab",'New Model Run'])
alt.themes.enable("streamlit")

# st.set_page_config(
#     page_title="Time series annotations", page_icon="⬇", layout="centered"
# )


with tab1:
   model_res_dash.gen_app()

with tab2:
   agent_app.gen_app_3()

with tab3:
   new_run.gen_app()