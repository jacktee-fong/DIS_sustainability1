import pandas as pd
from utility.prediction import predict_chronos
from utility.prediction import predict_lgbm

# Load the building data
df_building = pd.read_excel("store/train_data.xlsx")

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