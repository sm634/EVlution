import altair as alt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import glob

alt.themes.enable("streamlit")

st.set_page_config(
    page_title="Time series annotations", page_icon="⬇", layout="centered"
)


@st.experimental_memo
def get_data():
    names = glob.glob('Data/mdf*.csv')
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
    data_all
    return data_all

def data_subset(data_all):
    data = data_all[data_all['model_name'].isin(locs)]
    data['hour'] = pd.to_datetime(data.date_time).dt.hour
    data = data.groupby('hour').mean().reset_index()
    return data

@st.experimental_memo(ttl=60 * 60 * 24)
def get_chart(data):
    # hover = alt.selection_single(
    #     fields=["hour"],
    #     nearest=True,
    #     on="mouseover",
    #     empty="none",
    # )

    lines = (
        alt.Chart(data, height=500, title="Evolution of stock prices")
        .mark_line()
        .encode(
            x=alt.X("hour", title="hour"),
            y=alt.Y("charge_load", title="charge_load"),
            color="symbol",
        )
    )

    # Draw points on the line, and highlight based on selection
    # points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    # tooltips = (
    #     alt.Chart(data)
    #     .mark_rule()
    #     .encode(
    #         x="yearmonthdate(date_time)",
    #         y="price",
    #         opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
    #         tooltip=[
    #             alt.Tooltip("date_time", title="date_time"),
    #             alt.Tooltip("charge_load", title="charge_load"),
    #         ],
    #     )
    #     .add_selection(hover)
    # )

    return (lines ).interactive() #+ points)

source = get_data()

st.title("⬇ Time series annotations")

st.write("Give more context to your time series using annotations!")

col1, col2, col3 = st.columns(3)
with col1:
    # ticker = st.text_input("Choose a ticker (⬇💬👇ℹ️ ...)", value="⬇")#
    locs = [st.radio('locations', source['model_name'].unique(), index=0,)]

with col2:
    ticker_dx = st.slider(
        "Horizontal offset", min_value=-30, max_value=30, step=1, value=0
    )
with col3:
    ticker_dy = st.slider(
        "Vertical offset", min_value=-30, max_value=30, step=1, value=-10
    )

# Original time series chart. Omitted `get_chart` for clarity
data = data_subset(source)
print(data)
chart = get_chart(data)

# Input a
# Display both charts together
st.altair_chart(
    (chart).interactive(), use_container_width=True
)
st.map(source)

