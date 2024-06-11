import pandas as pd

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
        month = row['date']

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
    # extract year from the 'date' column
    year = row["date"].year

    # select the appropriate emission factor based on the variable and year
    if variable == "energy":
        factor_index = intensity[year]['grid_emission_factor']
        return row["energy"] * factor_index
    else:
        factor_index = intensity[year]['water_factor']
        return row["water"] * factor_index

