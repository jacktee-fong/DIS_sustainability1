import streamlit as st
from streamlit_utils.utils import st_get_all_building, st_get_basic_data
import os

IMAGE_PATH = "store/photo"

st.set_page_config(page_title="DIS Sustainability", page_icon=':star', layout='wide')

# Using "with" notation
with st.sidebar:
    code_selected = st.selectbox(
        "",
        st_get_all_building()
    )
    basic_data = st_get_basic_data("SGX1")
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

    wch_colour_box = (0, 204, 102)
    wch_colour_font = (0, 0, 0)
    fontsize = 18
    valign = "left"
    iconname = "fas fa-asterisk"
    sline = "Observations"
    lnk = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'
    i = 123

    htmlstr = f"""<p style='background-color: rgb({wch_colour_box[0]}, 
                                                      {wch_colour_box[1]}, 
                                                      {wch_colour_box[2]}, 0.75); 
                                color: rgb({wch_colour_font[0]}, 
                                           {wch_colour_font[1]}, 
                                           {wch_colour_font[2]}, 0.75); 
                                font-size: {fontsize}px; 
                                border-radius: 7px; 
                                padding-left: 12px; 
                                padding-top: 18px; 
                                padding-bottom: 18px; 
                                line-height:25px;'>
                                <i class='{iconname} fa-xs'></i> {i}
                                </style><BR><span style='font-size: 14px; 
                                margin-top: 0;'>{sline}</style></span></p>"""

    st.markdown(lnk + htmlstr, unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown(f'<div style="text-align: left;">Net Lettable Area:</div>', unsafe_allow_html=True)
    st.metric("Temperature", "70 °F", "1.2 °F")
    st.write(code_selected)

with col2:
    st.markdown(f'<div style="text-align: left;">Net Lettable Area:</div>', unsafe_allow_html=True)
    z = st.metric("Temperature", "70 °F", "1.2 °F")
    st.markdown(f'<div style="text-align: left;">{z}:</div>', unsafe_allow_html=True)
    st.write(code_selected)

    wch_colour_box = (0, 204, 102)
    wch_colour_font = (0, 0, 0)
    fontsize = 18
    valign = "left"
    iconname = "fas fa-asterisk"
    sline = "Observations"
    lnk = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'
    i = 123

    htmlstr = f"""<p style='background-color: rgb({wch_colour_box[0]}, 
                                                  {wch_colour_box[1]}, 
                                                  {wch_colour_box[2]}, 0.75); 
                            color: rgb({wch_colour_font[0]}, 
                                       {wch_colour_font[1]}, 
                                       {wch_colour_font[2]}, 0.75); 
                            font-size: {fontsize}px; 
                            border-radius: 7px; 
                            padding-left: 12px; 
                            padding-top: 18px; 
                            padding-bottom: 18px; 
                            line-height:25px;'>
                            <i class='{iconname} fa-xs'></i> {i}
                            </style><BR><span style='font-size: 14px; 
                            margin-top: 0;'>{sline}</style></span></p>"""

    st.markdown(lnk + htmlstr, unsafe_allow_html=True)
