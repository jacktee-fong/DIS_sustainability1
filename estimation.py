import lightgbm as lgb
import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
from utility.functions import calculate_working_days
import pickle

# Load the saved model
with open('model/lgbm_model.pkl', 'rb') as file:  
    model = pickle.load(file)

df_building = pd.read_excel("store/clean_data2.xlsx")

# historical data 
df_historical = df_building[df_building['codes'] == 'SGX C1 Energy & Water' ]
df_historical = df_historical[['month', 'codes', 'energy', 'working_day', 'temperature']]

# rename the month column to date
df_historical["date"] = df_historical["month"]
df_historical = df_historical.drop('month', axis=1)

# extract the month and year from the date column
df_historical["month"] = df_historical["date"].dt.month
df_historical["year"] = df_historical["date"].dt.year

# calculate the horizon of prediction
time_now = pd.Timestamp("2023-06-01")
max_possible_date = time_now + relativedelta(months=18)
if max_possible_date.month == 12:
    estimation_end = max_possible_date.replace(day=31).date()
else:
    estimation_end = max_possible_date.replace(year=max_possible_date.year - 1).replace(month=12).replace(day=31).date()

entry_last = df_historical['date'].iloc[-1]


# Generate range of future dates from last entry date up to estimation_end
future_dates = pd.date_range(start= entry_last + pd.DateOffset(days=1), end=estimation_end, freq='MS')

# Create a DataFrame for future dates
df_future = pd.DataFrame(future_dates, columns=['date'])
df_future['month'] = df_future['date']
df_future['temperature'] = np.random.randint(min(df_historical['temperature']), max(df_historical['temperature']))
df_future['year'] = df_future['date'].dt.year
df_future['codes'] = df_historical['codes']

# month column for calculation is in datetime
df_future = calculate_working_days(df_future)

# month column for feature is in int
df_future['month'] = df_future['date'].dt.month

# Prepare features for prediction
X_future = df_future[["month", "year", "working_day", "temperature"]]

# Predict
predictions = model.predict(X_future)

df_future['energy'] = predictions

print(df_future)

df_full = pd.concat([df_historical, df_future])

output_file_path = 'store/predict_data.xlsx'
df_full.to_excel(output_file_path, sheet_name="Summary", index=False)

