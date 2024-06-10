from datetime import datetime
import zoneinfo
import pandas as pd


def unix_to_datetime(x, tz_str):
    """
    convert unix timestamp to datetime object
    :param x: int = unix timestamp
    :param tz_str: str = timezone string
    :return: datetime object
    """
    timezone = zoneinfo.ZoneInfo(tz_str)
    local_time = datetime.fromtimestamp(x, timezone)
    return local_time

def get_model_data(model):
    """
    get the predicted data from Excel file based on the selected prediction model.
    :param model: str = "LGBM" or "Chronos"
    :return: dict of the dataset 
    """
    # initialize an empty DataFrame to store the combined data
    df_full = pd.DataFrame()

    # load the original dataset from an Excel file
    df = pd.read_excel("store/clean_data.xlsx")
    
    # check the model selected to retrieve the respective dataset 
    if model == "Chronos":
        df_predict = pd.read_excel("store/clean_data_chronos.xlsx")
    elif model == "LGBM":
        df_predict = pd.read_excel("store/clean_data_lgbm.xlsx")
    
    unique_codes = list(set(df_predict.code.to_list()))

    # combine the original data with predicted data for each code 
    for code in unique_codes:
        df_code = df[df["code"] == code]
        df_pred = df_predict[df_predict["code"] == code]
        # combine the row from both datasets
        df_combine= pd.concat([df_code, df_pred],ignore_index=True)
        # Append the combined data to df_full
        df_full = pd.concat([df_full, df_combine], ignore_index=True)
    
    return df_full.to_dict(orient='records')
