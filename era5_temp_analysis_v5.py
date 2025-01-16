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

# Create figure with three subplots
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

# Plot 1: Bara Mental Health Cases
bara_data = {'Season': ['Spring', 'Rest of Year'],
             'Cases': [4.5, 1.6]}
colors1 = ['#FF7F50', '#4169E1']
ax1.bar(bara_data['Season'], bara_data['Cases'], color=colors1)
ax1.set_title('Bara Mental Health Cases\nper Month')
ax1.set_ylabel('Average Cases per Month')
ax1.grid(axis='y', alpha=0.2)
ax1.text(0.05, -0.2, 'Source: CHBAH Maternity 2023-2024\nSpring diff: 3.0',
         transform=ax1.transAxes, fontsize=8, ha='left')

# Plot 2: Szabo Study Cases
szabo_data = {'Season': ['Spring', 'Rest of Year'],
              'Cases': [40, 36]}
ax2.bar(szabo_data['Season'], szabo_data['Cases'], color=colors1)
ax2.set_title('Szabo Study Cases\nper Month (1989)')
ax2.set_ylabel('Average Cases per Month')
ax2.grid(axis='y', alpha=0.2)
ax2.text(0.05, -0.2, 'Source: Szabo & Jones (1989)\nSpring diff: +4.7',
         transform=ax2.transAxes, fontsize=8, ha='left')

# Plot 3: ERA5 Temperature Change
transitions = [winter_spring, spring_summer]
labels = ['Winter to\nSpring', 'Spring to\nSummer']
colors = ['#FF7F50', '#4169E1']

bars = ax3.bar(range(len(transitions)), transitions, color=colors, width=0.6)

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f}°C',
             ha='center', va='bottom')

# Customize the plot
ax3.set_title('JHB Temperature Change\n(ERA5 2m Temperature)')
ax3.set_xticks(range(len(labels)))
ax3.set_xticklabels(labels)
ax3.set_ylabel('Temperature Change (°C)')
ax3.grid(axis='y', alpha=0.2)
ax3.set_ylim(0, 6.5)

# Add source and note information
ax3.text(0.05, -0.2, 
         'Source: ERA5 reanalysis (1989-2024)\nWinter-Spring rise: 6.4°C',
         transform=ax3.transAxes, fontsize=8, ha='left')

ax3.text(0.95, -0.25,
         'Note: SON = September, October, November (Southern Hemisphere Spring)\nTemperature from ERA5 2m air temperature reanalysis',
         transform=ax3.transAxes, fontsize=8, ha='right')

# Main title
plt.suptitle('Seasonal Comparison of Mental Health Cases in Johannesburg\nSpring (SON) vs Rest of Year',
             y=1.05, fontsize=14)

# Adjust layout
plt.tight_layout()

# Save figure
plt.savefig('paper_figures_color/seasonal_comparison_combined_v5.png',
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
