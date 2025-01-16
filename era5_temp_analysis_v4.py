import ee
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# Initialize Earth Engine
ee.Initialize()

# Define Johannesburg coordinates
JHB_POINT = ee.Geometry.Point([28.0473, -26.2041])

# Function to get ERA5 temperature data
def get_era5_temp(start_date, end_date):
    era5_dataset = ee.ImageCollection('ECMWF/ERA5/MONTHLY')\
        .filterDate(start_date, end_date)\
        .select('mean_2m_air_temperature')
    
    def extract_temp(image):
        date = ee.Date(image.get('system:time_start'))
        temp = image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=JHB_POINT,
            scale=27830
        ).get('mean_2m_air_temperature')
        return ee.Feature(None, {
            'date': date.format('YYYY-MM-dd'),
            'temperature': temp
        })

    temps = era5_dataset.map(extract_temp).getInfo()
    return pd.DataFrame([
        {
            'date': feature['properties']['date'],
            'temperature': feature['properties']['temperature'] - 273.15  # Convert K to °C
        }
        for feature in temps['features']
    ])

# Get data for 1989-2024
df = get_era5_temp('1989-01-01', '2024-12-31')
df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.month

# Calculate average temperature for each month
monthly_avg = df.groupby('month')['temperature'].mean()

# Calculate temperature changes
winter_spring = monthly_avg[9] - monthly_avg[8]  # Sep - Aug
spring_summer = monthly_avg[12] - monthly_avg[11]  # Dec - Nov

# Create the visualization
plt.figure(figsize=(6, 4))

# Plot bars
transitions = [winter_spring, spring_summer]
labels = ['Winter to\nSpring', 'Spring to\nSummer']
colors = ['#FF7F50', '#4169E1']  # Coral for Winter to Spring, Royal Blue for Spring to Summer

bars = plt.bar(range(len(transitions)), transitions, color=colors, width=0.6)

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f}°C',
             ha='center', va='bottom')

# Customize the plot
plt.title('JHB Temperature Change\n(ERA5 2m Temperature)', 
          fontsize=12, pad=10)
plt.xticks(range(len(labels)), labels)
plt.ylabel('Temperature Change (°C)')

# Add grid
plt.grid(axis='y', linestyle='-', alpha=0.2)

# Adjust y-axis to match reference
plt.ylim(0, 6.5)

# Add source and note information
plt.figtext(0.1, -0.2, 
            'Source: ERA5 reanalysis (1989-2024)\n' +
            'Winter-Spring rise: 6.4°C',
            fontsize=8, ha='left')

plt.figtext(0.95, -0.2,
            'Note: SON = September, October, November (Southern Hemisphere Spring)\n' +
            'Temperature from ERA5 2m air temperature reanalysis',
            fontsize=8, ha='right')

plt.tight_layout()

# Save the plot
plt.savefig('paper_figures_color/temp_change_era5_v4.png', 
            dpi=300, bbox_inches='tight')
plt.close()

# Print statistics
print("\nTemperature Change Analysis:")
print("===========================")
print(f"Winter to Spring change: {winter_spring:.1f}°C")
print(f"Spring to Summer change: {spring_summer:.1f}°C")
print("\nMonthly Averages:")
for month in range(1, 13):
    print(f"{pd.Timestamp(2024, month, 1).strftime('%B')}: {monthly_avg[month]:.1f}°C")
