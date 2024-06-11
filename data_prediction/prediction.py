import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
import pickle
from utility.functions import calculate_working_days, calculate_kpi
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
    :param df_building dataframe: dataframe that contains historical data for buildings
    :param time_now int: Unix timestamp represents the current time and used to define the starting point for future predictions
    :param tz_str str: timezone 
    Return: dataframe: dataframe that contains the predicted energy and water for future dates
    """
    # convert the UNIX timestamp to a datetime object with the specified timezone using the 'unix_to_datetime' function
    time_now = unix_to_datetime(time_now, tz_str)

    # Determine the prediction end date 18 months from the current time
    max_possible_date = time_now + relativedelta(months=18)

    # If the month of 'max_possible_date' is December, set the 'estimation_end' to December 31 of the same year
    # Otherwise set it to December 31 of the previous year to ensure the prediction period ends at the end of a year
    if max_possible_date.month == 12:
        estimation_end = max_possible_date.replace(day=31).date()
    else:
        estimation_end = max_possible_date.replace(year=max_possible_date.year - 1).replace(month=12).replace(day=31).date()

    # Initialize an empty DataFrame for future data
    resp_df = pd.DataFrame()

    # Get unique codes from the 'code_number' column of df_buidling 
    unique_codes = df_building['code_number'].unique()

    # Set a global random seed for consistency across function calls
    # make sure the temperature column has distinct data for each row 
    np.random.seed(84)

    # iterate through each unique building code to predict future data
    for code in unique_codes:

        # Filter the historical data ('df_building') for the current code.
        temp_hist = df_building[df_building['code_number'] == code]

        # Check if the filtered DataFrame is empty
        if temp_hist.empty:
            continue
        
        # get the last entry date by extracting the last row of 'date' column from 'temp_hist'
        entry_last = temp_hist['date'].iloc[-1]

        # create a list of future dates starting from the day after the last entry date and end at the 'estimation_end'
        future_dates = pd.date_range(start=entry_last + pd.DateOffset(days=1), end=estimation_end, freq='MS')

        # Create a temporary DataFrame to store the data for future dates
        # The temp_df will have following columns: 
        # - 'date': Future dates for which predictions are needed
        # - 'energy': Initialized to 0, will be updated with predicted values later
        # - 'water': Initialized to 0, will be updated with predicted values later
        # - 'working_day': Initialized to 0, will calculate the working days later
        # - 'temperature': Random temperatures within the historical range
        # - 'code_number': Provided code for all entries
        temp_df = pd.DataFrame({
            'date': future_dates,
            'energy':0, 'water':0, "working_day": 0, 
            'temperature': np.random.uniform(temp_hist['temperature'].min(), temp_hist['temperature'].max(),len(future_dates)),
            "code_number": code,
        })

        # Get the relevant details ('codes', 'code' and 'gfa') from the last historical entry
        temp_df['codes'] = temp_hist['codes'].iloc[-1]
        temp_df['code'] = temp_hist['code'].iloc[-1]
        temp_df['gfa'] = temp_hist['gfa'].iloc[-1]

        # extract the value of 'month' and 'year' from 'date' column
        temp_df['month'] = temp_df['date'].dt.month
        temp_df['year'] = temp_df['date'].dt.year

        temp_df.reset_index(drop=True, inplace=True)

        # Calculate working days for each 'date' by using the function 'calculate_working_days'
        temp_df = calculate_working_days(temp_df)

        # Concatenate the temp_df to the resp_df
        resp_df = pd.concat([resp_df, temp_df])
    
    resp_df.reset_index(drop=True, inplace=True)

    # Prepare features for prediction
    X_future = resp_df[["month", "year", "working_day", "temperature",  "code_number"]]

    # Load the pre-trained LightGBM models for energy and water
    energy = pickle.load(open("store/model/lgbm_energy_model.pkl", 'rb'))
    water = pickle.load(open("store/model/lgbm_water_model.pkl", 'rb'))

    # Predict 'energy' and 'water' for the future dates using the loaded model with the features selected
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
    :param df_building dataframe: dataframe that contains historical data for buildings
    :param time_now int: Unix timestamp represents the current time and used to define the starting point for future predictions
    :param tz_str str: timezone 
    Return: dataframe: dataframe that contains the predicted energy and water for future dates
    """
    # convert the UNIX timestamp to a datetime object with the specified timezone using the 'unix_to_datetime' function
    time_now = unix_to_datetime(time_now, tz_str)

    # Determine the prediction end date 18 months from the current time
    max_possible_date = time_now + relativedelta(months=18) 

    # If the month of 'max_possible_date' is December, set the 'estimation_end' to December 31 of the same year
    # Otherwise set it to December 31 of the previous year to ensure the prediction period ends at the end of a year
    if max_possible_date.month == 12:
        estimation_end = max_possible_date.replace(day=31).date()
    else:
        estimation_end = max_possible_date.replace(year=max_possible_date.year - 1).replace(month=12).replace(day=31).date()

    # Initialize an empty DataFrame to store predicted data
    resp_df = pd.DataFrame()

    # Get unique codes from the 'code_number' column of df_buidling 
    unique_codes = df_building['code_number'].unique()

    # iterate through each building code to get the predicted data for energy and water
    for code in unique_codes:

        # Extract historical data for the current building code
        temp_hist = df_building[df_building['code_number'] == code]

        # Check if the filtered DataFrame is empty
        if temp_hist.empty:
            continue
        
         # get the last entry date by extracting the last row of 'date' column from 'temp_hist'
        entry_last = temp_hist['date'].iloc[-1]

        # Set the prediction horizon based on the month difference between the last entry date and the end of estimation.
        # If the 'entry_last' and the 'estimation_end' are one year apart in December, set horizon to 12 months.
        if relativedelta(estimation_end, entry_last).months == 0 and relativedelta(estimation_end, entry_last).years == 1:
            horizon = 12
        else:
            horizon = relativedelta(estimation_end, entry_last).months

        # create an empty dict to store the relevant data 
        temp_dict = {"date": [], "energy": [], "water": [], "working_day": []}

        # iterate over each row in the temp_hist DataFrame
        # append the 'date', 'energy', 'water' and working_day' value from each row of temp_hist into temp_dict
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

        # Iterate over the length of the low_energy list
        for i in range(len(low_energy)):
            # Create a new row of data with the following:
            # - date: Increment the date of the last row in df_pred by 32 days and set the day to the 1st
            # - energy: Value from the low_energy list
            # - water: Value from the low_water list
            # - working_day: Initialized to 0, will calculate the working days later
            # - code_number: Use the provided code
            row_data = {"date": (df_pred.iloc[last_row_index]["date"] +
                                    timedelta(days=32)).replace(day=1),
                        "energy": low_energy[i], "water": low_water[i],
                        'working_day': 0,
                        "code_number": code}
            # Convert the items of row data into a DataFrame
            temp_df = pd.DataFrame(row_data.items())

            # Transpose the DataFrame to have columns as keys and rows as values
            temp_df = temp_df.T

            # Set the first row as the header
            temp_df.columns = temp_df.iloc[0]
            temp_df = temp_df.drop(index=0)

            # Add necessary data from the last row of temp_hist DataFrame
            temp_df['codes'] = temp_hist['codes'].iloc[-1]
            temp_df['code'] = temp_hist['code'].iloc[-1]
            temp_df['gfa'] = temp_hist['gfa'].iloc[-1]
            
            # Concatenate the temp_df to the resp_df
            resp_df = pd.concat(([resp_df, temp_df]))

            # Concatenate the temp_df to the df_pred DataFrame to keep track of the predictions
            df_pred = pd.concat([df_pred, temp_df])
            df_pred.reset_index(inplace=True, drop=True)

            # Increment the index for the last row 
            last_row_index += 1

    # Reset the index of the 'resp_df 'to ensure it starts from 0
    resp_df.reset_index(drop=True, inplace=True)

    # calculate the working days of resp_df for each month using 'calculate_working_day' function
    resp_df = calculate_working_days(resp_df)

    # Remove the unecessary column
    resp_df.drop(columns=['code_number'], inplace=True)

    # calculate KPI with the predicted data using 'calculate_kpi' function 
    final_df = calculate_kpi(resp_df)
    
    return final_df


