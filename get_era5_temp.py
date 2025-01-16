import ee
import pandas as pd
from datetime import datetime

# Initialize Earth Engine
ee.Initialize()

# Define Johannesburg coordinates
jhb_point = ee.Geometry.Point([28.0473, -26.2041])

# Load ERA5 monthly data
era5_monthly = ee.ImageCollection('ECMWF/ERA5/MONTHLY')

# Filter for temperature and time period (1989-present)
# Note: ERA5 data typically has some delay, so we'll get up to the latest available
era5_temp = era5_monthly.select('mean_2m_air_temperature').filterDate('1989-01-01', datetime.now().strftime('%Y-%m-%d'))

# Function to get monthly averages for specific periods
def get_period_temps(start_year, end_year, month):
    filtered = era5_temp.filter(ee.Filter.calendarRange(start_year, end_year, 'year')) \
                       .filter(ee.Filter.calendarRange(month, month, 'month'))
    mean_temp = filtered.mean()
    temp_value = mean_temp.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=jhb_point,
        scale=27830  # ERA5 spatial resolution
    ).get('mean_2m_air_temperature')
    return ee.Number(temp_value)

# Define periods based on our datasets
periods = {
    'Szabo (1989)': (1989, 1989),
    'UCT (2013-2019)': (2013, 2019),
    'Recent (2023-2024)': (2023, 2024),
    'All Years (1989-2024)': (1989, 2024)
}

months = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_nums = [8, 9, 10, 11, 12]

# Get temperatures for each period
for period_name, (start_year, end_year) in periods.items():
    print(f"\nERA5 Monthly Mean 2m Air Temperature for {period_name}:")
    temps = {}
    for month_name, month_num in zip(months, month_nums):
        try:
            temp_kelvin = get_period_temps(start_year, end_year, month_num).getInfo()
            temp_celsius = temp_kelvin - 273.15  # Convert Kelvin to Celsius
            temps[month_name] = round(temp_celsius, 1)
            print(f"{month_name}: {temps[month_name]}°C")
        except Exception as e:
            print(f"Could not get data for {month_name} in period {period_name}")
    
    if temps:  # Calculate and print temperature changes
        winter_spring_change = temps['Nov'] - temps['Aug']
        spring_summer_change = temps['Dec'] - temps['Nov']
        print(f"Winter to Spring change: {winter_spring_change:.1f}°C")
        print(f"Spring to Summer change: {spring_summer_change:.1f}°C")

# Save to file
with open('era5_temps_by_period.txt', 'w') as f:
    for period_name, (start_year, end_year) in periods.items():
        f.write(f"\n{period_name}:\n")
        temps = {}
        for month_name, month_num in zip(months, month_nums):
            try:
                temp_kelvin = get_period_temps(start_year, end_year, month_num).getInfo()
                temp_celsius = temp_kelvin - 273.15
                temps[month_name] = round(temp_celsius, 1)
                f.write(f"{month_name},{temps[month_name]}\n")
            except:
                continue
        
        if temps:
            winter_spring_change = temps['Nov'] - temps['Aug']
            spring_summer_change = temps['Dec'] - temps['Nov']
            f.write(f"Winter-Spring change,{winter_spring_change:.1f}\n")
            f.write(f"Spring-Summer change,{spring_summer_change:.1f}\n")
