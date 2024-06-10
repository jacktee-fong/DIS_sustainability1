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
    """
    Predict the value of energy and water for each building using the LGBM model from historical data.
    Parameters:
    df_building (DataFrame): A DataFrame that contains historical data for buildings
    time_now (int): Unix timestamp represents the current time and used to define the starting point for future predictions
    tz_str (str): timezone 
    Return: DataFrame: A DataFrame that contains the predicted energy and water for future dates
    """
    # convert the UNIX timestamp to a datetime object with the specified timezone.
    time_now = unix_to_datetime(time_now, tz_str)

    # Determine the prediction end date 18 months from the current time
    # If the end month is December, set the end date to December 31 of the same year
    # Otherwise set it to December 31 of the previous year to ensure the prediction period ends at the end of a year
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
    # make sure the temperature column has distinct data for each row 
    np.random.seed(84)

    # iterate through each unique building code to predict future data
    for code in unique_codes:

        # Filter the historical data for the current code.
        temp_hist = df_building[df_building['code_number'] == code]

        # Check if the filtered DataFrame is empty
        if temp_hist.empty:
            continue

        # Generate future dates starting from the day after the last entry date
        entry_last = temp_hist['date'].iloc[-1]
        future_dates = pd.date_range(start=entry_last + pd.DateOffset(days=1), end=estimation_end, freq='MS')

        # Create a temporary DataFrame to store the data for future dates
        temp_df = pd.DataFrame({
            'date': future_dates,
            'energy':0, 'water':0, "working_day": 0, 
            'temperature': np.random.uniform(temp_hist['temperature'].min(), temp_hist['temperature'].max(),len(future_dates)),
            "code_number": code,
        })

        # Get the relevant details from the last historical entry
        temp_df['codes'] = temp_hist['codes'].iloc[-1]
        temp_df['code'] = temp_hist['code'].iloc[-1]
        temp_df['gfa'] = temp_hist['gfa'].iloc[-1]
        temp_df['month'] = temp_df['date'].dt.month
        temp_df['year'] = temp_df['date'].dt.year

        temp_df.reset_index(drop=True, inplace=True)

        # Calculate working days for each 'date' 
        temp_df = calculate_working_days(temp_df)

        resp_df = pd.concat([resp_df, temp_df])
    
    resp_df.reset_index(drop=True, inplace=True)

    # Prepare features for prediction
    X_future = resp_df[["month", "year", "working_day", "temperature",  "code_number"]]

    # Load the pre-trained LightGBM models for energy and water
    energy = pickle.load(open("model/lgbm_energy_model.pkl", 'rb'))
    water = pickle.load(open("model/lgbm_water_model.pkl", 'rb'))

    # Predict 'energy' and 'water' for the future dates
    energy_pred = energy.predict(X_future)
    water_pred = water.predict(X_future)
    
    # update 'energy' and 'water' column with the predicted values
    resp_df['energy'] = energy_pred
    resp_df['water'] = water_pred

    # drop unnecessary columns to clean up the DataFrame
    resp_df.drop(columns=['temperature', 'month', 'year', 'code_number'], inplace=True)

    # calculate KPI with the predicted data
    final_df = calculate_kpi(resp_df)

    return final_df

def predict_chronos(df_building, time_now: int = 1685548800, tz_str: str = "Asia/Singapore"):
    """
    Predict the value of energy and water for each building using the Chronos model from historical data.
    Parameters:
    df_building (DataFrame): A DataFrame that contains historical data for buildings
    time_now (int): Unix timestamp represents the current time and used to define the starting point for future predictions
    tz_str (str): timezone 
    Return: DataFrame: A DataFrame that contains the predicted energy and water for future dates
    """
    time_now = unix_to_datetime(time_now, tz_str)

    # Determine the prediction end date 18 months from the current time
    # If the end month is December, set the end date to December 31 of the same year
    # Otherwise set it to December 31 of the previous year to ensure the prediction period ends at the end of a year
    max_possible_date = time_now + relativedelta(months=18)
    if max_possible_date.month == 12:
        estimation_end = max_possible_date.replace(day=31).date()
    else:
        estimation_end = max_possible_date.replace(year=max_possible_date.year - 1).replace(month=12).replace(day=31).date()

    # Initialize an empty DataFrame to store predicted data
    resp_df = pd.DataFrame()

    # Get unique codes
    unique_codes = df_building['code_number'].unique()

    for code in unique_codes:

        # Extract historical data for the current building code
        temp_hist = df_building[df_building['code_number'] == code]

        # Check if the filtered DataFrame is empty
        if temp_hist.empty:
            continue

        entry_last = temp_hist['date'].iloc[-1]

        # Set the prediction horizon based on the time difference to the end of the prediction period.
        # If the 'entry_last' and the 'estimation_end' are one year apart in December, set horizon to 12 months.
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

        # Convert the dict to DataFrame for model prediction
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
                        'working_day': 0,
                        "code_number": code}
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

    print(resp_df.head())

    resp_df.reset_index(drop=True, inplace=True)

    # calculate the working days for each month
    resp_df = calculate_working_days(resp_df)
    print(resp_df.head()) 

    # Remove the unecessary column
    resp_df.drop(columns=['code_number'], inplace=True)

    final_df = calculate_kpi(resp_df)
    
    return final_df


