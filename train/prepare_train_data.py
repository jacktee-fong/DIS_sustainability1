import pandas as pd

# Load the building data
df_building = pd.read_excel("store/input/clean_data.xlsx")
df_temperature = pd.read_excel("store/input/temperature_data.xlsx")

df_building['date'] = pd.to_datetime(df_building['date'], format='%Y-%m')  
df_temperature['date'] = pd.to_datetime(df_temperature['date'], format='%Y-%m')

# Merge the DataFrames on the 'month' column
df_building = pd.merge(df_building, df_temperature, on='date', how='left')

unique_codes = df_building['code'].unique()
code_number = {code: i + 1 for i, code in enumerate(unique_codes)}

# Assign numbers to the 'code' column using the dictionary
df_building['code_number'] = df_building['code'].map(code_number)

output_file_path = 'store/input/train_data.xlsx'
df_building.to_excel(output_file_path, sheet_name="Summary", index=False)