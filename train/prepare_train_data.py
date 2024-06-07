import pandas as pd

# Load the building data
df_building = pd.read_excel("store/clean_data.xlsx")
df_temperature = pd.read_excel("store/temperature_data.xlsx")

df_building['month'] = pd.to_datetime(df_building['month'], format='%Y-%m')  
df_temperature['month'] = pd.to_datetime(df_temperature['month'], format='%Y-%m')

# Merge the DataFrames on the 'month' column
df_building = pd.merge(df_building, df_temperature, on='month', how='left')

unique_codes = df_building['code'].unique()
code_number = {code: i + 1 for i, code in enumerate(unique_codes)}

# Assign numbers to the 'code' column using the dictionary
df_building['code_number'] = df_building['code'].map(code_number)

print(df_building)
output_file_path = 'store/train_data.xlsx'
df_building.to_excel(output_file_path, sheet_name="Summary", index=False)