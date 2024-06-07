import requests
import json
from tools.general_utils import unix_to_datetime
from apps.schemas import BuildingDataResponse, KPICardResponse, GeneralInput, MonitoringDataResponse
from tools.code_dict import icon_dict, kpi_dict
import time
import matplotlib.pyplot as plt
import random


BASE_URL = "http://127.0.0.1:9001"


def st_get_all_building():
    """
    get all building name from backend
    :return: {"name_list": ["building1", "building2"], "code_list": ["code1", "code2"]}
    """
    z = requests.get(url=BASE_URL + "/dis_api/allBuildingName",
                     headers={
                         'accept': 'application/json',
                         'Content-Type': 'application/json'},
                     json={}
                     )
    return json.loads(z.content)


def st_get_basic_data(code):
    """
    get basic data from backend
    :param code: building code
    :return: BuildingDataResponse
    """
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
    """
    get data to display the kpi card
    :param theme_mode: str = "dark" or "light"
    :param kpi: str = "water" or "energy"
    :param code: str = "SGX1" or "SGX2" or ...
    :return: html string
    """

    # check the theme mode to set the card background and font color
    if theme_mode:
        wch_colour_box = (0, 0, 0)
        wch_colour_font = (255, 255, 255)
    else:
        wch_colour_box = (250, 251, 252)
        wch_colour_font = (0, 0, 0)

    # obtain the icon to display in the card
    kpi_icon = icon_dict[kpi]

    # obtain the unit and name to display in the card
    if kpi == "water":
        kpi_str = "Water"
        kpi_unit = " m3/month"
    elif kpi == "energy":
        kpi_str = "Electricity"
        kpi_unit = " kwh/month"

    # Obtain data from backend
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

    # obtain the data for comparison
    sub_line1 = f"{data.kpi_current:.1f}"
    sub_line2 = f"{data.different:.1%}"

    # obtain the color code to display, according to positive or negative value
    if data.different < 0:
        color_set = "green"
    else:
        color_set = "red"

    lnk = ('<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" '
           'crossorigin="anonymous">')

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
                               margin-top: 0;'>{sub_line1}</style></span><span>{kpi_unit}</span><BR><BR>
                               <span style='font-size: 20px; color: {color_set};
                               margin-top: 0;'>{sub_line2}</style></span><span>&nbsp;</span>
                               <span style='font-size: 20px;'>from last year</span>
                               </p>"""

    return lnk + htmlstr


def get_monitoring_data(payload: GeneralInput):
    """
    get monitoring data from backend
    :param payload: GeneralInput
    :return: a matplotlib figure
    """
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

    # get the time now to calculate which month to cutoff
    time_now = unix_to_datetime(payload.time_now, payload.tz_str)
    cutoff_count = time_now.month

    # plotting matplotlib figure, first set the figure size
    fig, ax = plt.subplots(figsize=(6, 6))

    # give the title and label name
    plt.xlabel("Date")
    plt.ylabel(kpi_dict[payload.kpi]["unit"], fontsize=10)
    plt.title(kpi_dict[payload.kpi]["name"] + " Consumption", fontsize=10)

    # get the data, need to separate the same line into 2 part, history till now is solid, and prediction is dotted
    x1 = data.x[0:cutoff_count]
    y1 = data.y[0:cutoff_count]
    x2 = data.x[cutoff_count - 1:]
    y2 = data.y[cutoff_count - 1:]
    plt.plot(x1, y1, marker='o', color=kpi_dict[payload.kpi]["color"],
             linewidth=2, label=payload.kpi)
    plt.plot(x2, y2, marker='o', color=kpi_dict[payload.kpi]["color"],
             linewidth=2, linestyle='--')

    # x-axis label rotate 45 degree
    plt.xticks(rotation=45, ha='right')

    # plot legend
    plt.legend()
    return fig


def st_get_benchmark(payload: GeneralInput):
    """
    Get benchmark data from backend. The benchmark only compare the data in years.
    :param payload: GeneralInput
    :return: matplotlib figure
    """
    z = requests.get(url=BASE_URL + "/dis_api/BenchmarkChart",
                     headers={
                         'accept': 'application/json',
                         'Content-Type': 'application/json'},
                     json={
                         "code": payload.code,
                         "time_now": payload.time_now,
                         "kpi": payload.kpi,
                     }
                     )
    data = json.loads(z.content)

    # plotting matplotlib figure, first set the figure size
    fig, ax = plt.subplots(figsize=(15, 15))

    # give the title and label name
    plt.xlabel("Year")
    plt.ylabel(data["unit"], fontsize=10)
    plt.title(kpi_dict[payload.kpi]["name"] + " Benchmark", fontsize=10)

    # get x-axis to plot. It is always the same.
    x1 = data["x"][0:data["cutOff"]]
    x2 = data["x"][data["cutOff"] - 1:]

    # get a list of building to iterate through to plot the graph
    building_list = st_get_all_building()["code_list"]

    # this is a list of keys that we will skip.
    ignore_list = ["x", "cutOffYear", "cutOff", "unit"]

    # iterate through every key in data. If it is a building, we plot it. The benchmark is treated separately
    for keys in data.keys():
        if keys in building_list:
            # get the value for plotting graph. y1 is solid line and y2 is for dotted line
            y1 = data[keys][0:data["cutOff"]]
            y2 = data[keys][data["cutOff"] - 1:]

            # the color is random for each building
            color_random = (random.random(), random.random(), random.random())
            plt.plot(x1, y1, marker='o', color=color_random, linewidth=2, label=keys)
            plt.plot(x2, y2, marker='o', color=color_random, linewidth=2, linestyle='--')

        # if this is the benchmark (not building and not belong to the ignore list)
        elif keys not in ignore_list:
            y1 = data[keys][0:data["cutOff"]]
            y2 = data[keys][data["cutOff"] - 1:]

            # the color is getting from the pre-defined dictionary
            plt.plot(x1, y1, marker='o', color=kpi_dict[payload.kpi]["color"], linewidth=2,
                     label=f"{keys} Benchmark")
            plt.plot(x2, y2, marker='o', color=kpi_dict[payload.kpi]["color"], linewidth=2, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    return fig

