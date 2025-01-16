import ee
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import YearLocator
import os

# Initialize Earth Engine
ee.Initialize()

# Define Rahima Moosa Hospital coordinates
RMMC_POINT = ee.Geometry.Point([27.9126, -26.1751])

# Function to get ERA5 daily temperature data
def get_era5_temp(start_date, end_date):
    # Process data year by year to avoid the 5000 element limit
    start_year = int(start_date.split('-')[0])
    end_year = int(end_date.split('-')[0])
    
    all_data = []
    for year in range(start_year, end_year + 1):
        year_start = f"{year}-01-01"
        year_end = f"{year}-12-31"
        
        era5_dataset = ee.ImageCollection('ECMWF/ERA5/DAILY')\
            .filterDate(year_start, year_end)\
            .select('maximum_2m_air_temperature')
        
        def extract_temp(image):
            date = ee.Date(image.get('system:time_start'))
            temp = image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=RMMC_POINT,
                scale=27830
            ).get('maximum_2m_air_temperature')
            return ee.Feature(None, {
                'date': date.format('YYYY-MM-dd'),
                'temperature': temp
            })

        temps = era5_dataset.map(extract_temp).getInfo()
        year_data = pd.DataFrame([
            {
                'date': feature['properties']['date'],
                'temperature': feature['properties']['temperature'] - 273.15  # Convert K to °C
            }
            for feature in temps['features']
        ])
        all_data.append(year_data)
        
    return pd.concat(all_data, ignore_index=True)

# Get baseline period data (1981-2010 is commonly used as climate baseline)
df_baseline = get_era5_temp('1981-01-01', '2010-12-31')
df_baseline['date'] = pd.to_datetime(df_baseline['date'])

# Calculate 90th percentile threshold for each day of the year
df_baseline['dayofyear'] = df_baseline['date'].dt.dayofyear
threshold_90th = df_baseline.groupby('dayofyear')['temperature'].quantile(0.9)

# Get recent period data for comparison (now only up to 2019 to avoid partial year)
df_recent = get_era5_temp('2011-01-01', '2019-12-31')
df_recent['date'] = pd.to_datetime(df_recent['date'])
df_recent['dayofyear'] = df_recent['date'].dt.dayofyear

# Add data completeness check
print("\nData Coverage:")
print("Data range:", df_recent['date'].min().strftime('%Y-%m-%d'), "to", df_recent['date'].max().strftime('%Y-%m-%d'))
print("\nDays per year:")
for year in range(2011, 2020):
    year_data = df_recent[df_recent['date'].dt.year == year]
    print(f"{year}: {len(year_data)} days")

# Add threshold to recent data
df_recent['threshold'] = df_recent['dayofyear'].map(threshold_90th)

# Identify days above 90th percentile
df_recent['above_90th'] = df_recent['temperature'] > df_recent['threshold']

# Calculate heat waves (2 or more consecutive days above 90th percentile)
df_recent['heatwave'] = False
for i in range(1, len(df_recent)):
    if df_recent['above_90th'].iloc[i] and df_recent['above_90th'].iloc[i-1]:
        df_recent.loc[df_recent.index[i-1:i+1], 'heatwave'] = True

# Calculate statistics
days_above_90th_per_year = df_recent['above_90th'].mean() * 365.25
heatwave_days_per_year = df_recent['heatwave'].mean() * 365.25

# Count number of distinct heat waves
heatwave_starts = 0
in_heatwave = False
for above_90th in df_recent['above_90th']:
    if above_90th and not in_heatwave:
        heatwave_starts += 1
        in_heatwave = True
    elif not above_90th:
        in_heatwave = False

years_analyzed = (df_recent['date'].max() - df_recent['date'].min()).days / 365.25
heatwaves_per_year = heatwave_starts / years_analyzed

# Create output directory
output_dir = 'heatwave_analysis'
os.makedirs(output_dir, exist_ok=True)

# Save the data
df_baseline.to_csv(os.path.join(output_dir, 'rmmc_baseline_temps.csv'), index=False)
df_recent.to_csv(os.path.join(output_dir, 'rmmc_recent_temps.csv'), index=False)

# Create visualizations
plt.style.use('seaborn-v0_8')

# Figure 1: Temperature Distribution Comparison
plt.figure(figsize=(12, 6))
sns.kdeplot(data=df_baseline, x='temperature', label='Baseline (1981-2010)', alpha=0.6)
sns.kdeplot(data=df_recent, x='temperature', label='Recent (2011-2019)', alpha=0.6)
plt.axvline(threshold_90th.mean(), color='r', linestyle='--', label='90th Percentile Threshold')
plt.title('Temperature Distribution at Rahima Moosa Hospital')
plt.xlabel('Maximum Daily Temperature (°C)')
plt.ylabel('Density')
plt.legend()
plt.savefig(os.path.join(output_dir, 'temperature_distribution.png'), dpi=300, bbox_inches='tight')
plt.close()

# Figure 2: Heat Wave Events Over Time
plt.figure(figsize=(15, 6))
annual_heatwaves = df_recent.groupby(df_recent['date'].dt.year)['heatwave'].sum()
print("\nAnnual Heat Wave Days by Year:")
for year, days in annual_heatwaves.items():
    print(f"{year}: {days:.1f} days")

plt.bar(annual_heatwaves.index, annual_heatwaves.values)
plt.title('Annual Heat Wave Days at Rahima Moosa Hospital (2011-2019)')
plt.xlabel('Year')
plt.ylabel('Number of Heat Wave Days')
plt.axhline(y=heatwave_days_per_year, color='r', linestyle='--', label=f'Average ({heatwave_days_per_year:.1f} days)')
plt.legend()
plt.savefig(os.path.join(output_dir, 'annual_heatwaves.png'), dpi=300, bbox_inches='tight')
plt.close()

# Figure 3: Monthly Distribution of Heat Wave Days
plt.figure(figsize=(12, 6))
monthly_heatwaves = df_recent.groupby(df_recent['date'].dt.month)['heatwave'].mean() * 30.44  # Average days per month
plt.bar(range(1, 13), monthly_heatwaves.values)
plt.title('Average Heat Wave Days per Month at Rahima Moosa Hospital (2011-2019)')
plt.xlabel('Month')
plt.ylabel('Average Days with Heat Wave Conditions')
plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
plt.savefig(os.path.join(output_dir, 'monthly_heatwaves.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"\nHeat Wave Analysis for Rahima Moosa Mother and Child Hospital")
print(f"Using baseline period 1981-2010 for threshold calculation")
print(f"\nResults for recent period (2011-2019):")
print(f"Days above 90th percentile per year: {days_above_90th_per_year:.1f}")
print(f"Heat wave days per year: {heatwave_days_per_year:.1f}")
print(f"Number of heat waves per year: {heatwaves_per_year:.1f}")
print(f"\nNote: Heat wave defined as 2+ consecutive days above 90th percentile threshold")
print(f"\nData and visualizations have been saved to '{output_dir}' folder:")
print(f"- {output_dir}/rmmc_baseline_temps.csv")
print(f"- {output_dir}/rmmc_recent_temps.csv")
print(f"- {output_dir}/temperature_distribution.png")
print(f"- {output_dir}/annual_heatwaves.png")
print(f"- {output_dir}/monthly_heatwaves.png")

# Additional verification statistics
print("\nVerification Statistics:")
print(f"Baseline period mean temperature: {df_baseline['temperature'].mean():.1f}°C")
print(f"Recent period mean temperature: {df_recent['temperature'].mean():.1f}°C")
print(f"90th percentile threshold: {threshold_90th.mean():.1f}°C")
print(f"Number of baseline days: {len(df_baseline)}")
print(f"Number of recent days: {len(df_recent)}")
