import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# Set the style for all plots
plt.style.use('default')  # Use default style instead of seaborn
sns.set_theme(style="whitegrid")  # Add seaborn grid

# Function to calculate seasonal averages
def calculate_seasonal_stats(data, date_column, count_column=None, by_year=False):
    # If date_column contains datetime objects, extract month
    if pd.api.types.is_datetime64_any_dtype(data[date_column]):
        data['month'] = data[date_column].dt.month
    else:
        # If date_column already contains month numbers
        data['month'] = data[date_column]
    
    # Define spring vs rest of year (Southern Hemisphere)
    spring_months = [9, 10, 11]        # Sep through Nov
    rest_months = [12, 1, 2, 3, 4, 5, 6, 7, 8]  # Dec through Aug
    
    if by_year:
        # Group by year and calculate seasonal averages
        years = data['year'].unique()
        yearly_stats = []
        for year in years:
            year_data = data[data['year'] == year]
            spring_avg = year_data[year_data['month'].isin(spring_months)][count_column].mean()
            rest_avg = year_data[year_data['month'].isin(rest_months)][count_column].mean()
            yearly_stats.append({
                'year': year,
                'spring_avg': spring_avg,
                'rest_avg': rest_avg,
                'difference': spring_avg - rest_avg
            })
        return pd.DataFrame(yearly_stats)
    else:
        # Calculate overall averages
        if count_column is None:
            spring_cases = len(data[data['month'].isin(spring_months)]) / 3
            rest_cases = len(data[data['month'].isin(rest_months)]) / 9
        else:
            spring_cases = data[data['month'].isin(spring_months)][count_column].mean()
            rest_cases = data[data['month'].isin(rest_months)][count_column].mean()
        return spring_cases, rest_cases

# Load Bara data
bara_data = pd.read_excel("c:/Users/CraigParker/OneDrive - Wits Health Consortium/PHR PC/Downloads/Joburg/paper_figures_color/datasets/10122024 mental health issues in obstetrics final final.xlsx")
print("Bara data columns:", bara_data.columns.tolist())

# Create figure with subplots (1x3 grid)
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

# Colors
spring_color = '#FF6B35'    # Warm orange for spring
rest_color = '#4575B4'    # Cool blue for rest of year

# 1. Bara Data Analysis
spring_bara, rest_bara = calculate_seasonal_stats(bara_data, 'date')
ax1.bar(['Spring', 'Rest of Year'], 
        [spring_bara, rest_bara], 
        color=[spring_color, rest_color])
ax1.set_title('Bara Mental Health Cases\nper Month')
ax1.set_ylabel('Average Cases per Month')
ax1.text(0.05, -0.15, 'Source: CHBAH Maternity 2023-2024\nSpring diff: {:.1f}'.format(spring_bara - rest_bara), 
         transform=ax1.transAxes, fontsize=8, va='top')

# 2. Szabo Data Analysis
szabo_monthly = pd.DataFrame([
    {'month': 1, 'admissions': 30},
    {'month': 2, 'admissions': 35},
    {'month': 3, 'admissions': 40},
    {'month': 4, 'admissions': 32},
    {'month': 5, 'admissions': 35},
    {'month': 6, 'admissions': 45},
    {'month': 7, 'admissions': 38},
    {'month': 8, 'admissions': 40},
    {'month': 9, 'admissions': 35},
    {'month': 10, 'admissions': 42},
    {'month': 11, 'admissions': 47},
    {'month': 12, 'admissions': 35}
])
spring_szabo, rest_szabo = calculate_seasonal_stats(szabo_monthly, 'month', 'admissions')
ax2.bar(['Spring', 'Rest of Year'],
        [spring_szabo, rest_szabo],
        color=[spring_color, rest_color])
ax2.set_title('Szabo Study Cases\nper Month (1989)')
ax2.set_ylabel('Average Cases per Month')
ax2.text(0.05, -0.15, 'Source: Szabo & Jones (1989)\nSpring diff: +{:.1f}'.format(spring_szabo - rest_szabo), 
         transform=ax2.transAxes, fontsize=8, va='top')

# 3. Temperature Differential Analysis (ERA5 data)
# ERA5 monthly mean 2m temperature for Johannesburg (1989-2024)
era5_temps = {
    'Aug': 13.5,  # Late winter
    'Sep': 17.4,  # Early spring
    'Oct': 19.2,  # Mid spring
    'Nov': 19.9,  # Late spring
    'Dec': 20.7   # Early summer
}

# Calculate temperature changes
spring_temp_rise = era5_temps['Nov'] - era5_temps['Aug']  # Winter to Spring
other_temp_rise = era5_temps['Dec'] - era5_temps['Nov']   # Spring to Summer

ax3.bar(['Winter to\nSpring', 'Spring to\nSummer'], 
        [spring_temp_rise, other_temp_rise],
        color=[spring_color, rest_color])
ax3.set_title('JHB Temperature Change\n(ERA5 2m Temperature)')
ax3.set_ylabel('Temperature Change (°C)')
ax3.text(0.05, -0.15, 'Source: ERA5 reanalysis (1989-2024)\nWinter-Spring rise: {:.1f}°C'.format(spring_temp_rise), 
         transform=ax3.transAxes, fontsize=8, va='top')

# Add overall figure title and notes
fig.suptitle('Seasonal Comparison of Mental Health Cases in Johannesburg\nSpring (SON) vs Rest of Year', 
             fontsize=14, y=1.02)
fig.text(0.99, 0.01, 'Note: SON = September, October, November (Southern Hemisphere Spring)\nTemperature from ERA5 2m air temperature reanalysis',
         fontsize=8, ha='right', va='bottom')

# Adjust layout and save
plt.tight_layout()
plt.savefig('seasonal_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# Print temperature change details
print("\nERA5 Temperature Analysis:")
print(f"Winter (Aug) to Spring (Nov) change: {spring_temp_rise:.1f}°C")
print(f"Spring (Nov) to Summer (Dec) change: {other_temp_rise:.1f}°C")
