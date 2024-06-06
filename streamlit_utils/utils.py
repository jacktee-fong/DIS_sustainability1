import requests
import json
from tools.general_utils import unix_to_datetime
from apps.schemas import BuildingDataResponse, KPICardResponse, GeneralInput, MonitoringDataResponse
from streamlit_utils.code_dict import icon_dict, kpi_dict
import time
import matplotlib.pyplot as plt
import pandas as pd

BASE_URL = "http://127.0.0.1:9001"


def st_get_all_building():
    z = requests.get(url=BASE_URL + "/dis_api/allBuildingName",
                     headers={
                         'accept': 'application/json',
                         'Content-Type': 'application/json'},
                     json={}
                     )
    return json.loads(z.content)["name_list"]


def st_get_basic_data(code):
    z = requests.get(url=BASE_URL + "/dis_api/buildingData",
                     headers={
                         'accept': 'application/json',
                         'Content-Type': 'application/json'},
                     json={
                         "code": code
                     }
                     )
    return BuildingDataResponse(**dict(json.loads(z.content)))


def kpi_card(theme_mode, kpi, code):
    if theme_mode:
        wch_colour_box = (0, 0, 0)
        wch_colour_font = (255, 255, 255)
    else:
        wch_colour_box = (250, 251, 252)
        wch_colour_font = (0, 0, 0)

    kpi_icon = icon_dict[kpi]
    if kpi == "water":
        kpi_str = "Water"
        kpi_unit = " m3/month"
    elif kpi == "energy":
        kpi_str = "Electricity"
        kpi_unit = " kwh/month"
    data = requests.get(url=BASE_URL + "/dis_api/KPICardData",
                     headers={
                         'accept': 'application/json',
                         'Content-Type': 'application/json'},
                     json={
                         "code": code,
                         "time_now": int(time.time()),
                         "kpi": kpi
                     }
                     )
    data = KPICardResponse(**dict(json.loads(data.content)))
    sline = f"{data.kpi_current:.1f}"
    sline1 = f"{data.different:.1%}"
    if data.different < 0:
        color_set = "green"
    else:
        color_set = "red"
    lnk = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'

    htmlstr = f"""<p style='background-color: rgb({wch_colour_box[0]}, 
                                                     {wch_colour_box[1]}, 
                                                     {wch_colour_box[2]}); 
                               color: rgb({wch_colour_font[0]}, 
                                          {wch_colour_font[1]}, 
                                          {wch_colour_font[2]},); 
                               font-size: 24px;
                               border-color: red; 
                               border-radius: 12px; 
                               padding-left: 12px; 
                               padding-top: 18px; 
                               padding-bottom: 18px; 
                               line-height:25px;'>
                               <i class='{kpi_icon} fa-xs'></i> {kpi_str}
                               </style><BR><BR><span style='font-size: 32px; 
                               margin-top: 0;'>{sline}</style></span><span>{kpi_unit}</span><BR><BR>
                               <span style='font-size: 20px; color: {color_set};
                               margin-top: 0;'>{sline1}</style></span><span>&nbsp;</span>
                               <span style='font-size: 20px;'>from last year</span>
                               </p>"""

    return lnk + htmlstr


def get_monitoring_data(payload: GeneralInput):
    z = requests.get(url=BASE_URL + "/dis_api/MonitoringData",
                     headers={
                         'accept': 'application/json',
                         'Content-Type': 'application/json'},
                     json={
                         "code": payload.code,
                         "time_now": payload.time_now,
                         "kpi": payload.kpi,
                     }
                     )
    data = MonitoringDataResponse(**dict(json.loads(z.content)))
    time_now = unix_to_datetime(payload.time_now, payload.tz_str)
    cutoff_count = time_now.month

    fig, ax = plt.subplots(figsize=(6, 6))
    plt.xlabel("Date")
    plt.ylabel(kpi_dict[payload.kpi]["unit"], fontsize=10)
    plt.title(kpi_dict[payload.kpi]["name"] + " Consumption", fontsize=10)
    x1 = data.x[0:cutoff_count]
    y1 = data.y[0:cutoff_count]
    x2 = data.x[cutoff_count -1:]
    y2 = data.y[cutoff_count -1:]
    plt.plot(x1, y1, marker='o', color=kpi_dict[payload.kpi]["color"],
             linewidth=2)
    plt.plot(x2, y2, marker='o', color=kpi_dict[payload.kpi]["color"],
             linewidth=2, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    return fig
