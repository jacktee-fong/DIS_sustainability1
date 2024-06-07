from fastapi import APIRouter, HTTPException
from tools.general_utils import unix_to_datetime
import pandas as pd
from apps.schemas import BuildingDataResponse, GeneralInput, KPICardResponse, MonitoringDataResponse
from tools.code_dict import benchmark_dict
import json


router = APIRouter()


@router.get('/allBuildingName', response_model=dict)
def get_all_building_name():
    """
    get all building name and code from Excel file
    :return: dict = {"name_list": list, "code_list": list}
    """
    df = pd.read_excel("store/basic_data.xlsx")
    name_list = df.name.to_list()
    code_list = df.code.to_list()
    return {"name_list": name_list, "code_list": code_list}


@router.get('/buildingData', response_model=BuildingDataResponse)
def get_building_data(payload: GeneralInput):
    """
    get building data from Excel file
    :param payload: GeneralInput
    :return: BuildingDataResponse
    """
    df = pd.read_excel("store/basic_data.xlsx")

    # get the data into dictionary
    data_dict = df[df["code"] == payload.code].to_dict(orient='records')[0]

    # the box is a list of lat long, but it is saved as string because it comes from Excel.
    # use json to load it into a list
    data_dict["box"] = json.loads(data_dict["box"])

    # some of the carkpark is str and some of it is int, this is to standardize
    data_dict["carpark"] = str(data_dict["carpark"])

    # get the dictionary into the response schema
    resp = BuildingDataResponse(**dict(data_dict))
    print(resp)
    return resp


@router.get('/KPICardData', response_model=KPICardResponse)
def get_kpi_card_data(payload: GeneralInput):
    """
    Get kpi card data from Excel file
    :param payload: GeneralInput
    :return: KPICardResponse
    """
    # get the current date and last year date
    time_now = unix_to_datetime(payload.time_now, payload.tz_str)
    date_now = time_now.replace(day=1)
    date_last_year = time_now.replace(day=1).replace(year=date_now.year - 1)

    # read the data from Excel and filter it accordingly
    df = pd.read_excel("store/clean_data.xlsx")
    df_code = df[df["code"] == payload.code]

    # make sure this column is a datetime format
    df_code["month"] = pd.to_datetime(df_code["month"])

    # set the month as index, so we could use loc to select data within the range
    df_code.set_index("month", inplace=True, drop=True)

    # obtain the data of current and last year and calculate the different
    kpi_current = df_code.loc[date_now.strftime('%Y-%m-%d')][payload.kpi]
    kpi_last_year = df_code.loc[date_last_year.strftime('%Y-%m-%d')][payload.kpi]
    different = (kpi_current - kpi_last_year) / kpi_last_year

    # put the response into schemas
    resp = KPICardResponse(kpi_current=kpi_current, kpi_last_year=kpi_last_year, different=different, kpi=payload.kpi)
    return resp


@router.get('/MonitoringData', response_model=MonitoringDataResponse)
def get_monitoring_data(payload: GeneralInput):
    """
    Get monitoring data from Excel file. Assume this is monthly data.
    :param payload: GeneralInput
    :return: MonitoringDataResponse
    """
    # get the dates of the years we are in, and calculate the first and last days of the year
    time_now = unix_to_datetime(payload.time_now, payload.tz_str)
    year_start = time_now.replace(day=1).replace(month=1).strftime('%Y-%m-%d')
    year_end = time_now.replace(month=12).replace(day=31).strftime('%Y-%m-%d')

    # get the data of the building that we want to see
    df = pd.read_excel("store/clean_data.xlsx")
    df_code = df[df["code"] == payload.code]

    # set the month as index, so we could use date to select the time range
    df_code.set_index("month", inplace=True, drop=True)
    df_chart = df_code.loc[year_start:year_end]
    df_chart.reset_index(inplace=True)

    # convert datetime object to date only to display on chart
    df_chart["date"] = pd.to_datetime(df_chart["month"]).dt.floor('D')

    # this is the x-axis data (date)
    date_list = df_chart["date"].to_list()
    resp = {"x": []}

    # convert the date object to date string to send over json
    for item in date_list:
        resp["x"].append(item.strftime('%Y-%m-%d'))

    # the y-axis is the data that we interested (such as "energy", "water")
    resp["y"] = df_chart[payload.kpi].to_list()

    # return the kpi that requested (mainly for troubleshooting use)
    resp["kpi"] = payload.kpi
    return resp


@router.get('/BenchmarkChart', response_model=dict)
def get_benchmark_chart(payload: GeneralInput):
    """
    Get benchmark chart data from Excel file. Assume this is yearly data.
    :param payload: GeneralInput
    :return: dict = {"x": list, "cutOffYear": int, "cutOff": int, "unit": str, building_data: list}
    """
    # if the kpi selected is not Benchmark, raise HttpException error
    if payload.kpi not in benchmark_dict.keys():
        raise HTTPException(status_code=404, detail="Kpi selected is not benchmark")

    # get the current year to calculate the cutoff
    year_now = unix_to_datetime(payload.time_now, payload.tz_str).year
    df = pd.read_excel("store/clean_data.xlsx")

    # make sure the column "month" is datetime
    df["month"] = pd.to_datetime(df["month"])

    # find out the unique code from the list to iterate through
    unique_codes = list(set(df.code.to_list()))

    # TODO: currently hardcode the year. Can change the code to obtain earlier and latest year to generate the list
    benchmark_year_list = [2018, 2019, 2020, 2021, 2022, 2023, 2024]

    # these are the standard data that needed to send over as response
    resp = {"x": benchmark_year_list,
            'cutOffYear': year_now,
            'cutOff': benchmark_year_list.index(year_now),
            "unit": benchmark_dict[payload.kpi]["year_unit"]}

    # initialise empty dictionary to hold data
    data = {}

    # filter and obtain the list of energy_obj based on the year selected
    for obj in unique_codes:
        data[obj] = []
        df_codes = df[df["code"] == obj]
        df_codes.set_index("month", inplace=True)

        # iterate through every year to obtain the sum or average data
        for year in resp["x"]:

            # the temp_list contain data for each year. This is because some of the benchmark need to be sum and
            # some of the benchmark needed to be average
            temp_list = df_codes.loc[f"{year}-01-01":f"{year}-12-13"]

            # check the kpi dict to seek the sum or average operation, and obtain the benchmark data if available
            if benchmark_dict[payload.kpi]["type"] == "AVERAGE":
                kpi = temp_list[payload.kpi].mean()
            elif benchmark_dict[payload.kpi]["type"] == "SUM":
                kpi = temp_list[payload.kpi].sum()
            if not pd.isna(kpi):
                data[obj].append(kpi)
            else:
                # TODO: what to do when kpi is null
                # temporary set it to 0
                data[obj].append(0)

    # append the benchmark to response
    if len(benchmark_dict[payload.kpi]["benchmark"]) > 0:
        for keys, values in benchmark_dict[payload.kpi]["benchmark"].items():
            resp[keys] = values

    # sort the building in orders before append it to response
    data1 = dict(sorted(data.items(), key=lambda item: (item[1][-1] is None, item[1][-1])))
    data_iter = iter(data1)
    for i in range(len(data1)):
        keys = next(data_iter)
        resp[keys] = data1[keys]
    return resp
