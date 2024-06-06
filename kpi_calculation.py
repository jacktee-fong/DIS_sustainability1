import pandas as pd
from utility.functions import calculate_carbon

# read and load the necessary excel file 
df_building = pd.read_excel("store/clean_data.xlsx")
df_basic = pd.read_excel("store/basic_data.xlsx")

# set "tab" as index for easier checking with the "codes" 
df_basic.set_index("tab", inplace=True)
data_basic = df_basic.to_dict(orient="index")

df_intensity = pd.read_excel("store/basic_data.xlsx", sheet_name='power')
df_intensity.set_index("year", inplace=True)
data_intensity = df_intensity.to_dict(orient='index')

# Create a list to hold the mean temperature for each sheet
mean_temperature = []

# Calculate mean temperature for each sheet just once
for year in range(2018, 2025):
    for month in range(1, 13):
        # Stop after February 2024
        if year == 2024 and month > 2:  
            break
        sheet_name = f"{year}{month:02d}"
        df_weather = pd.read_excel("store/Weather_Data_Newton_2018_to_2024.xlsx", sheet_name=sheet_name)
        df_weather['Mean Temperature (°C)'] = pd.to_numeric(df_weather['Mean Temperature (°C)'], errors='coerce')
        mean_temp = df_weather['Mean Temperature (°C)'].mean()
        mean_temperature.append(mean_temp)

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
        df_building.at[index, 'WEI'] = row['water'] * 1000 / (estimated_staff + 0.25 * estimated_visitors) / row['working_day']

        # Calculate carbon emissions
        df_building.at[index, 'carbon_energy'] = calculate_carbon(row, 'energy', data_intensity)
        df_building.at[index, 'carbon_water'] = calculate_carbon(row, 'water', data_intensity)
        df_building.at[index, 'carbon_index'] = (df_building.at[index, 'carbon_water'] + df_building.at[index, 'carbon_energy']) / data_building['gfa'] / (estimated_staff 
                                                                                                                                                           + 0.25 * estimated_visitors) * 10000

        # The len for mean_temperature is for one building so it is needed to insert the mean_temperature cyclically
        # Calculate the alt_index by taking the modulus of the current index with the length of mean_temperature
        # This makes the index wrap around if it goes beyond the length of the list
        alt_index = index % len(mean_temperature)

        # Use the alt_index to access elements in mean_temperature cyclically
        df_building.at[index, 'temperature'] = mean_temperature[alt_index]

output_file_path = 'store/clean_data2.xlsx'
df_building.to_excel(output_file_path, sheet_name="Summary", index=False)
