import requests
import json
from apps.schemas import BuildingDataResponse


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
                         "code": "SGX1"
                     }
                     )
    return BuildingDataResponse(**dict(json.loads(z.content)))
