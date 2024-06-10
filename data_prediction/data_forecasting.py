import pandas as pd
from data_prediction.prediction import predict_chronos
from data_prediction.prediction import predict_lgbm

# Load the building data
df_building = pd.read_excel("store/predict/train_data.xlsx")

# predict energy and water using lgbm model
df_lgbm = predict_lgbm(df_building)
print(df_lgbm.info())
output_file_path = 'store/output/clean_data_lgbm.xlsx'
df_lgbm.to_excel(output_file_path, sheet_name="Summary", index=False)

# predict energy and water using chronos
df_chronos = predict_chronos(df_building)
print(df_chronos.info())
output_file_path = 'store/output/clean_data_chronos.xlsx'
df_chronos.to_excel(output_file_path, sheet_name="Summary", index=False)