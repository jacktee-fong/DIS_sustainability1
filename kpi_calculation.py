import pandas as pd
from utility.functions import calculate_carbon

# read and load the necessary excel file 
df_building = pd.read_excel("store/output/clean_data.xlsx")
df_basic = pd.read_excel("store/input/basic_data.xlsx")

# set "tab" as index for easier checking with the "codes" 
df_basic.set_index("tab", inplace=True)
data_basic = df_basic.to_dict(orient="index")

df_intensity = pd.read_excel("store/input/basic_data.xlsx", sheet_name='power')
df_intensity.set_index("year", inplace=True)
data_intensity = df_intensity.to_dict(orient='index')

# To update the df_building by adding "EUI", "WEI" and "carbon_index" column
# iterate through the row of df_building to calculate the value of each kpi
# insert the calculated value at the specified index row by row  
for index, row in df_building.iterrows():
    code = row['codes']
    data_building = data_basic.get(code)

    # check if the "codes" in df_building matches the "tab" in data_basic to get the "gfa" value
    if data_building:
        # Calculate EUI
        df_building.at[index, 'EUI'] = row['energy'] / data_building['gfa']

        # assume that the number of staff per m^2 is 9.2 
        # assume that the number of visitors is 10% of the staff 
        # Calculate WEI
        estimated_staff = data_building['gfa'] / 9.2
        estimated_visitors = 0.10 * estimated_staff
        df_building.at[index, 'WEI_Area'] = row['water'] * 1000 / data_building['gfa']
        df_building.at[index, 'WEI_People'] = row['water'] * 1000 / (estimated_staff + 0.25 * estimated_visitors) / row['working_day']

        # Calculate carbon emissions
        df_building.at[index, 'carbon_energy'] = calculate_carbon(row, 'energy', data_intensity)
        df_building.at[index, 'carbon_water'] = calculate_carbon(row, 'water', data_intensity)
        df_building.at[index, 'carbon_index'] = (df_building.at[index, 'carbon_water'] + df_building.at[index, 'carbon_energy']) / data_building['gfa'] / (estimated_staff 
                                                                                                                                                           + 0.25 * estimated_visitors) * 10000

output_file_path = 'store/output/clean_data.xlsx'
df_building.to_excel(output_file_path, sheet_name="Summary", index=False)
