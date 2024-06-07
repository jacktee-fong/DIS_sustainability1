import pandas as pd
import numpy as np
from datetime import datetime
import zoneinfo
import torch

df_holiday = pd.read_excel("../MOM_PublicHoliday.xlsx")

def calculate_working_days(dataframe):
    """
    Calculates the number of working days for each month in a DataFrame.
    Args: dataframe: A DataFrame with a 'month' column containing datetime objects.
    Returns: A DataFrame with the same index as the input DataFrame, containing a
    'working_days' column with the number of working days for each month.
    """
    # create a dataframe to store the calculated 'working_day' for each month by intializing the value as 0 
    dataframe['working_day'] = 0

    # iterate through the input dataframe to calculate the 'working_day' for each month
    # remove the public holidays from all the weekdays for each month of the year 
    for index, row in dataframe.iterrows():
        month = row['month']

        start_date = month.replace(day=1)
        end_date = start_date + pd.offsets.MonthEnd(0)

        # create a list of weekdays (exclude weekends)
        weekdays = pd.date_range(start_date, end_date, freq='B')

        # check the holiays by matching the month and year from the df_holiday which store all the public holidays
        holidays = df_holiday[(df_holiday['Date'].dt.month == month.month) & (df_holiday['Date'].dt.year == month.year)]

        working_days = len(weekdays) - len(holidays)

        # assign the calculated 'working_days' to 'working_day' column for corresponding row 
        dataframe.at[index, 'working_day'] = working_days
    return dataframe

def calculate_carbon(row, variable, intensity):
    """
    Calculate the carbon emissions for a given row of data based on 'energy' and 'water'.
    Args:
    row: An object represents a row of dataframe that includes key like month, energy and water. 
    variable: A string as the type of variable to calculate emissions for 'energy' or 'water'.
    intensity: A dictionary with the value'grid_emission_factor' for energy and 'water_factor' for water.
    Returns: A float that calculated carbon emissions based on the input row, variable and intensity.
    """
    year = row["month"].year
    if variable == "energy":
        factor_index = intensity[year]['grid_emission_factor']
        return row["energy"] * factor_index
    else:
        factor_index = intensity[year]['water_factor']
        return row["water"] * factor_index
    
def unix_to_datetime(x, tz_str):
    timezone = zoneinfo.ZoneInfo(tz_str)
    local_time = datetime.fromtimestamp(x, timezone)
    return local_time


def chronos_forecast(model, data, horizon, target, quantiles):
    # Prepare the context
    context = torch.tensor(data[target].values, dtype=torch.float32)
    context = context.unsqueeze(0)  # Add batch dimension

    # Predict the next 'horizon' data points
    forecast = model.predict(context, horizon)  # shape [num_series, num_samples, horizon]

    # Extract quantiles for forecast
    low, median, high = np.quantile(forecast[0].numpy(), quantiles, axis=0)
    
    return low, median, high



