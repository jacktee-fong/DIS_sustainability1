import pandas as pd
import datetime
from utility.functions import calculate_working_days

# read and load the necessary excel file 
df_basic = pd.read_excel("store/basic_data.xlsx")

# set the "code" column as the index for dataframe for easier retrieve rows by index
df_basic.set_index("code", inplace=True)

# convert dataframe to dictionary with the index as key and the row data as value 
# easy access to row data by using the "code" as key
data_basic = df_basic.to_dict(orient="index")

dataframe_building = {}

# iterate through each item in data_basic for easier retrieval of relevant details
# "codes" as key and "details" as value 
for codes, details in data_basic.items():
    data_building = data_basic[codes]

    # skip the first 11 rows to get the data needed 
    df_building = pd.read_excel("store/singland mock.xlsx", sheet_name=data_building['tab'], skiprows=11)

    # only keep columns that have value
    df_building = df_building[['Month',
                               'Total building energy consumption (TBEC) (kWh/month)',
                               'Total water consumption (m3/mth)', 'No of Working days']]

    # rename the columns
    df_building.columns = ["month", "energy", "water", "working_day"]

    # check if the value is a date to ensure data consistency in the "Month" column 
    # drop all the rows where the "Month" column is not date
    z = df_building.to_dict("dict")
    row_to_drop = []
    for keys, values in z["month"].items():
        if not isinstance(values, datetime.datetime):
            row_to_drop.append(keys)
    df_building = df_building.drop(index=row_to_drop)

    # drop na/missing value based on energy and water 
    # to ensure the data used for analysis is complete and accurate
    df_building.dropna(subset=['energy', 'water'], inplace=True)

    # reset the dataframe index by dropping the old index
    df_building.reset_index(inplace=True, drop=True)

    # calculate working days within each month. Exclude every Saturday, Sunday, and public holiday
    # use the function 'calculate_working_days' which import from utility 
    df_building = calculate_working_days(df_building)

    # store df_building to dataframe_building with the respective sheetname
    dataframe_building[data_building['tab']] = df_building

# combine all DataFrames into a single DataFrame 
# making all the data easier to manage and manipulate
combined_df = pd.concat(dataframe_building.values(), ignore_index=True)

output_file_path = 'store/clean_data.xlsx'
combined_df.to_excel(output_file_path, sheet_name="Summary", index=False)
