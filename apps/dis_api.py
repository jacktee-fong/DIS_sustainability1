from fastapi import APIRouter, HTTPException
from tools.general_utils import unix_to_datetime
import pandas as pd
from apps.schemas import BuildingDataResponse, GeneralInput, KPICardResponse, MonitoringDataResponse
import json


router = APIRouter()


@router.get('/allBuildingName')
def get_all_building_name():
    df = pd.read_excel("store/basic_data.xlsx")
    name_list = df.name.to_list()
    return {"name_list": name_list}


@router.get('/buildingData', response_model=BuildingDataResponse)
def get_building_data(payload: GeneralInput):
    df = pd.read_excel("store/basic_data.xlsx")
    data_dict = df[df["code"] == payload.code].to_dict(orient='records')[0]
    data_dict["box"] = json.loads(data_dict["box"])
    data_dict["carpark"] = str(data_dict["carpark"])
    resp = BuildingDataResponse(**dict(data_dict))
    print(resp)
    return resp


@router.get('/KPICardData', response_model=KPICardResponse)
def get_kpi_card_data(payload: GeneralInput):
    time_now = unix_to_datetime(payload.time_now, payload.tz_str)
    date_now = time_now.replace(day=1)
    date_last_year = time_now.replace(day=1).replace(year=date_now.year - 1)
    df = pd.read_excel("store/clean_data.xlsx")
    df_code = df[df["code"] == payload.code]
    df_code["month"] = pd.to_datetime(df_code["month"])
    df_code.set_index("month", inplace=True, drop=True)
    kpi_current = df_code.loc[date_now.strftime('%Y-%m-%d')][payload.kpi]
    kpi_last_year = df_code.loc[date_last_year.strftime('%Y-%m-%d')][payload.kpi]
    different = (kpi_current - kpi_last_year) / kpi_last_year
    resp = KPICardResponse(kpi_current=kpi_current, kpi_last_year=kpi_last_year, different=different, kpi=payload.kpi)
    return resp


@router.get('/MonitoringData', response_model=MonitoringDataResponse)
def get_monitoring_data(payload: GeneralInput):
    time_now = unix_to_datetime(payload.time_now, payload.tz_str)
    year_start = time_now.replace(day=1).replace(month=1).strftime('%Y-%m-%d')
    year_end = time_now.replace(month=12).replace(day=31).strftime('%Y-%m-%d')
    df = pd.read_excel("store/clean_data.xlsx")
    df_code = df[df["code"] == payload.code]
    df_code.set_index("month", inplace=True, drop=True)
    df_chart = df_code.loc[year_start:year_end]
    df_chart.reset_index(inplace=True)
    df_chart["date"] = pd.to_datetime(df_chart["month"]).dt.floor('D')
    date_list = df_chart["date"].to_list()
    resp = {"x": []}
    for item in date_list:
        resp["x"].append(item.strftime('%Y-%m-%d'))
    resp["y"] = df_chart[payload.kpi].to_list()
    resp["kpi"] = payload.kpi

    return resp
