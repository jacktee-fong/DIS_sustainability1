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

from utility.prediction import predict_chronos
from utility.prediction import predict_lgbm

df_historical = df_building[['month', 'code_number', 'energy', 'water', 'working_day', 'temperature']]
df_historical = df_historical.copy()
# rename the month column to date
df_historical.rename(columns = {'month': 'date'}, inplace=True)
df_historical['date'] = pd.to_datetime(df_historical['date'])
# extract the month and year from the date column
df_historical["month"] = df_historical["date"].dt.month
df_historical["year"] = df_historical["date"].dt.year

# predict energy and water using lgbm model
df_lgbm = predict_lgbm(df_historical)
output_file_path = 'store/predict_lgbm_data.xlsx'
df_lgbm.to_excel(output_file_path, sheet_name="Summary", index=False)

# predict energy and water using chronos
df_chronos = predict_chronos(df_historical,)
print(df_chronos)
output_file_path = 'store/predict_chronos_data.xlsx'
df_chronos.to_excel(output_file_path, sheet_name="Summary", index=False)