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

# this is to set the page title and layout
st.set_page_config(page_title="DIS Sustainability", page_icon=':star', layout='wide')

# obtain the theme of the browser
theme_base = st_theme()
if theme_base["base"] == "dark":
    theme_dark = True
else:
    theme_dark = False

# Sidebar show the basic information on the building selected by user
with st.sidebar:
    # let user select the building for the dashboard
    code_selected = st.selectbox(
        "Please select a building",
        st_get_all_building()["name_list"]
    )
    code = code_dict[code_selected]

    # populate the basic data information in the sidebar
    basic_data = st_get_basic_data(code)
    st.write(basic_data.address)
    image_path = os.path.join(IMAGE_PATH, basic_data.photo)
    st.image(image_path)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f'<div style="text-align: left;">Net Lettable Area:</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: left;">Typical Floor Area(s):</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: left;">Nearest MRT Station(s):</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: left;">Nearest MRT Station(s):</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: left;">No. of Carpark Lots:</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div style="text-align: right;">{basic_data.net_area} sq ft</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: right;">{basic_data.floor}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: right;">{basic_data.net_area}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: right;">{basic_data.net_area}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: right;">{basic_data.net_area}</div>', unsafe_allow_html=True)


# this is the main body content
st.markdown(f'<div style="text-align: center; font-size: 42px">Monitoring Data</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown(kpi_card(theme_mode=theme_dark, kpi="energy", code=code), unsafe_allow_html=True)
    data = GeneralInput(code=code, kpi="energy", time_now=int(time.time()))
    st.pyplot(get_monitoring_data(data), use_container_width=True)

with col2:
    st.markdown(kpi_card(theme_mode=theme_dark, kpi="water", code=code), unsafe_allow_html=True)
    data = GeneralInput(code=code, kpi="water", time_now=int(time.time()))
    st.pyplot(get_monitoring_data(data))

st.markdown(f'<div style="text-align: center; font-size: 42px"></div>', unsafe_allow_html=True)
st.markdown(f'<div style="text-align: center; font-size: 42px">Benchmark Comparison</div>', unsafe_allow_html=True)

for benchmark in ["EUI", "WEI_Area", "WEI_People"]:
    data = GeneralInput(code=code, kpi=benchmark, time_now=int(time.time()))
    st.pyplot(st_get_benchmark(data))
