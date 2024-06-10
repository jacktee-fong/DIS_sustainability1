import pandas as pd

# Create a dict to hold the date and mean temperature for each sheet
data = []

# Calculate mean temperature for each sheet just once
for year in range(2018, 2025):
    for month in range(1, 13):
        # Stop after April 2024
        if year == 2024 and month > 4:
            break
        sheet_name = f"{year}{month:02d}"
        try:
            df_weather = pd.read_excel("store/input/Weather_Data_Newton_2018_to_2024.xlsx", sheet_name=sheet_name)
            df_weather['Mean Temperature (°C)'] = pd.to_numeric(df_weather['Mean Temperature (°C)'], errors='coerce')
            mean_temp = df_weather['Mean Temperature (°C)'].mean()
            # Append the year, month, and mean temperature to the list
            data.append({'date': f"{year}-{month:02d}", 'temperature': mean_temp})
        except Exception as e:
            print(f"Failed to process {sheet_name}: {e}")

# Convert the list of dictionaries to a DataFrame
df_temperature = pd.DataFrame(data)

output_file_path = 'store/predict/temperature_data.xlsx'
df_temperature.to_excel(output_file_path, index=False)
