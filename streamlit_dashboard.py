import time
import streamlit as st
from streamlit_utils.utils import (st_get_all_building, st_get_basic_data, kpi_card, get_monitoring_data,
                                   st_get_benchmark)
from tools.code_dict import code_dict
from streamlit_theme import st_theme
from apps.schemas import GeneralInput
import os


# set up the basic config and parameter
IMAGE_PATH = "store/photo"

# Use st.set_page_config to set up the title, icon, and layout of the Streamlit application
# this is to set the page title and layout
st.set_page_config(page_title="DIS Sustainability", page_icon=':star', layout='wide')

# obtain the theme of the browser
# Use the custom st_theme() function to get the current theme settings of the browser
theme_base = st_theme()

# Check the base theme to determine if it is dark or light
# If the base theme is "dark", set theme_dark to True
# Otherwise, set theme_dark to False
if theme_base["base"] == "dark":
    theme_dark = True
else:
    theme_dark = False

# Use the sidebar to allow the user to select a building and model for prediction
with st.sidebar:
    # create a dopdown list to let user select the building for the dashboard 
    # add label for the dropdown 
    # get the 'name_list' of building from the backend using 'st_get_all_building()'
    code_selected = st.selectbox(
        "Please select a building",
        st_get_all_building()["name_list"]
    )

    # Convert the selected building name to its corresponding code 
    # Lookup the code for the selected building name in 'code_dict'
    code = code_dict[code_selected]

    # Let the user select a model for prediction
    # add label for the dropdown
    # add the options ("LGBM", "Chronos") for prediction models
    model_selected = st.selectbox(
        "Please select a model to predict",
        ("LGBM", "Chronos")
    )

    # populate the basic data information in the sidebar
    # retrieve basic data for the selected building using its code
    basic_data = st_get_basic_data(code)

    # print and display basic building information
    st.write(basic_data.address)

    # construct the path to the building photo
    image_path = os.path.join(IMAGE_PATH, basic_data.photo)
    # Display building image
    st.image(image_path)

    # Use columns to display additional building information
    # create two columns with a 2:1 width ratio
    col1, col2 = st.columns([2, 1])

    with col1:
        # display labels for building information
        st.markdown(f'<div style="text-align: left;">Net Lettable Area:</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: left;">Typical Floor Area(s):</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: left;">Nearest MRT Station(s):</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: left;">Nearest MRT Station(s):</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: left;">No. of Carpark Lots:</div>', unsafe_allow_html=True)
    with col2:
        # display values for building information
        st.markdown(f'<div style="text-align: right;">{basic_data.net_area} sq ft</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: right;">{basic_data.floor}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: right;">{basic_data.net_area}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: right;">{basic_data.net_area}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: right;">{basic_data.net_area}</div>', unsafe_allow_html=True)


# this is the main body content

# display a title for the monitoring data section
st.markdown(f'<div style="text-align: center; font-size: 42px">Monitoring Data</div>', unsafe_allow_html=True)

# use columns to display KPI cards and corresponding monitoring data plots
# create two equal-width columns
col1, col2 = st.columns([1, 1])

with col1:
    # display KPI card for energy
    # use the kpi_card function to generate the KPI card 
    st.markdown(kpi_card(theme_mode=theme_dark, kpi="energy", code=code, model = model_selected), unsafe_allow_html=True)
    
    # prepare data to plot the chart for energy 
    data = GeneralInput(code=code, kpi="energy", time_now=int(time.time()), model = model_selected)
    
    # display the energy monitoring plot
    # generate the plot using the 'get_monitoring_data' function by passing in 'data'
    # ensure the plot fits the column width
    st.pyplot(get_monitoring_data(data), use_container_width=True)

with col2:
    # display KPI card for water
    # use the kpi_card function to generate the KPI card 
    st.markdown(kpi_card(theme_mode=theme_dark, kpi="water", code=code, model=model_selected), unsafe_allow_html=True)
    
    # prepare data to plot the chart for water 
    data = GeneralInput(code=code, kpi="water", time_now=int(time.time()), model = model_selected)
    
    # display the water monitoring plot
    # generate the plot using the 'get_monitoring_data' function by passing in 'data'
    st.pyplot(get_monitoring_data(data))

# Display a title for the benchmark comparison section
st.markdown(f'<div style="text-align: center; font-size: 42px">Benchmark Comparison</div>', unsafe_allow_html=True)

# Let the user select a benchmark for comparison
benchmark = st.selectbox(
        "Please select a benchmark",
        ("EUI", "WEI_Area", "WEI_People", "carbon_index","carbon_energy", "carbon_water")
    )

# prepare data for the benchmark comparison plot
data = GeneralInput(code=code, kpi=benchmark, time_now=int(time.time()), model = model_selected)

# display the benchmark comparison plot
# generate the plot using the 'st_get_benchmark' function by passing in 'data'
st.pyplot(st_get_benchmark(data))
