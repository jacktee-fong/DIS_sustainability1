from fastapi import Depends, APIRouter, HTTPException, UploadFile, File, Form
import pandas as pd
from apps.schemas import BuildingDataResponse
import json

router = APIRouter()


@router.get('/allBuildingName')
def get_all_building_name():
    df = pd.read_excel("store/basic_data.xlsx")
    name_list = df.name.to_list()
    return {"name_list": name_list}


@router.get('/buildingData', response_model=BuildingDataResponse)
def get_building_data():
    df = pd.read_excel("store/basic_data.xlsx")
    data_dict = df[df["code"] == "SGX1"].to_dict(orient='records')[0]
    data_dict["box"] = json.loads(data_dict["box"])
    resp = BuildingDataResponse(**dict(data_dict))
    return resp
