import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
import pickle
from utility.functions import calculate_working_days
from utility.functions import calculate_kpi
from utility.functions import unix_to_datetime
from utility.functions import chronos_forecast
from datetime import timedelta
import torch
from chronos import ChronosPipeline

pipelines = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-small",
    device_map="cuda" if torch.cuda.is_available() else "cpu",
    torch_dtype=torch.float32  # Using float32 for more precision in quantiles
)

def predict_lgbm(df_building, time_now: int = 1685548800, tz_str: str = "Asia/Singapore", ):

    # Calculate the horizon of prediction
    time_now = unix_to_datetime(time_now, tz_str)
    max_possible_date = time_now + relativedelta(months=18)
    if max_possible_date.month == 12:
        estimation_end = max_possible_date.replace(day=31).date()
    else:
        estimation_end = max_possible_date.replace(year=max_possible_date.year - 1).replace(month=12).replace(day=31).date()

    # Initialize an empty DataFrame for future data
    resp_df = pd.DataFrame()

    # Get unique codes
    unique_codes = df_building['code_number'].unique()

    # Set a global random seed for consistency across function calls
    np.random.seed(84)

    # Loop through each code to create the future DataFrame
    for code in unique_codes:
        # Generate future dates
        temp_hist = df_building[df_building['code_number'] == code]

        # Check if the filtered DataFrame is empty
        if temp_hist.empty:
            continue

        entry_last = temp_hist['date'].iloc[-1]
        future_dates = pd.date_range(start=entry_last + pd.DateOffset(days=1), end=estimation_end, freq='MS')

        temp_df = pd.DataFrame({
            'date': future_dates,
            'energy':0, 'water':0, "working_day": 0, 
            'temperature': np.random.uniform(temp_hist['temperature'].min(), temp_hist['temperature'].max(),len(future_dates)),
            "code_number": code,
        })
        temp_df['codes'] = temp_hist['codes'].iloc[-1]
        temp_df['code'] = temp_hist['code'].iloc[-1]
        temp_df['gfa'] = temp_hist['gfa'].iloc[-1]
        temp_df['month'] = temp_df['date'].dt.month
        temp_df['year'] = temp_df['date'].dt.year

        temp_df.reset_index(drop=True, inplace=True)

        temp_df = calculate_working_days(temp_df)

        resp_df = pd.concat([resp_df, temp_df])
    
    resp_df.reset_index(drop=True, inplace=True)

    # Prepare features for prediction
    X_future = resp_df[["month", "year", "working_day", "temperature",  "code_number"]]

    energy = pickle.load(open("model/lgbm_energy_model.pkl", 'rb'))
    water = pickle.load(open("model/lgbm_water_model.pkl", 'rb'))

    # calculate the prediction for energy and water
    energy_pred = energy.predict(X_future)
    water_pred = water.predict(X_future)
    
    resp_df['energy'] = energy_pred
    resp_df['water'] = water_pred

    resp_df.drop(columns=['temperature', 'month', 'year'], inplace=True)

    resp_df = calculate_kpi(resp_df)

    return resp_df

def predict_chronos(df_building, time_now: int = 1685548800, tz_str: str = "Asia/Singapore"):
    # calculate the horizon of prediction
    time_now = unix_to_datetime(time_now, tz_str)
    max_possible_date = time_now + relativedelta(months=18)
    if max_possible_date.month == 12:
        estimation_end = max_possible_date.replace(day=31).date()
    else:
        estimation_end = max_possible_date.replace(year=max_possible_date.year - 1).replace(month=12).replace(day=31).date()

    resp_df = pd.DataFrame()

    # Get unique codes
    unique_codes = df_building['code_number'].unique()

    for code in unique_codes:

        temp_hist = df_building[df_building['code_number'] == code]

        # Check if the filtered DataFrame is empty
        if temp_hist.empty:
            continue

        entry_last = temp_hist['date'].iloc[-1]

        # if the last entry date has the same month but one year different as estimation_end 
        # set the horizon to 12 (one year)
        if relativedelta(estimation_end, entry_last).months == 0 and relativedelta(estimation_end, entry_last).years == 1:
            horizon = 12
        else:
            horizon = relativedelta(estimation_end, entry_last).months

        # create a dataframe to contain the data, energy and water data
        temp_dict = {"date": [], "energy": [], "water": [], "working_day": []}

        # Append the data into the dictionary from each row
        for _, row in temp_hist.iterrows():
            temp_dict["date"].append(row['date'])
            temp_dict["energy"].append(row['energy'])
            temp_dict["water"].append(row['water'])
            temp_dict["working_day"].append(row['working_day'])

        df_pred = pd.DataFrame(temp_dict)

        # calculate the prediction for energy and water using chronos foundation model from AWS
        low_energy, mid_energy, high_energy = chronos_forecast(model=pipelines, data=df_pred,horizon=horizon,
                                                            target="energy", quantiles=[0.3, 0.5, 0.7])
        low_water, mid_water, high_water = chronos_forecast(model=pipelines, data=df_pred, horizon=horizon,
                                                            target="water", quantiles=[0.3, 0.5, 0.7])

        # create the response dataframe
        df_pred.reset_index(inplace=True, drop=True)
        last_row_index = df_pred.index[-1]

        for i in range(len(low_energy)):
            row_data = {"date": (df_pred.iloc[last_row_index]["date"] +
                                    timedelta(days=32)).replace(day=1),
                        "energy": low_energy[i], "water": low_water[i],
                        "working_day": 0, "code_number": code}
            temp_df = pd.DataFrame(row_data.items())
            temp_df = temp_df.T
            temp_df.columns = temp_df.iloc[0]
            temp_df = temp_df.drop(index=0)
            temp_df['codes'] = temp_hist['codes'].iloc[-1]
            temp_df['code'] = temp_hist['code'].iloc[-1]
            temp_df['gfa'] = temp_hist['gfa'].iloc[-1]
            resp_df = pd.concat(([resp_df, temp_df]))
            df_pred = pd.concat([df_pred, temp_df])
            df_pred.reset_index(inplace=True, drop=True)
            last_row_index += 1

    # calculate the working days of each month
    resp_df = calculate_working_days(resp_df)
    resp_df = calculate_kpi(resp_df)
    return resp_df


