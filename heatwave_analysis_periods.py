import ee
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Initialize Earth Engine
ee.Initialize()

# Define Rahima Moosa Hospital coordinates
RMMC_POINT = ee.Geometry.Point([28.0183, -26.1752])

def get_era5_temp(start_date, end_date):
    # Process data year by year to avoid the 5000 element limit
    start_year = int(start_date.split('-')[0])
    end_year = int(end_date.split('-')[0])
    
    all_data = []
    for year in range(start_year, end_year + 1):
        print(f"Processing ERA5 data for year {year}...")
        year_start = f"{year}-01-01"
        year_end = f"{year}-12-31"
        
        era5_dataset = ee.ImageCollection('ECMWF/ERA5/DAILY')\
            .filterDate(year_start, year_end)\
            .select('maximum_2m_air_temperature')
        
        def extract_temp(image):
            date = ee.Date(image.get('system:time_start'))
            temp = image.reduceRegion(
                reducer=ee.Reducer.max(),  # Use max instead of mean
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
        
    df = pd.concat(all_data, ignore_index=True)
    df['date'] = pd.to_datetime(df['date'])
    return df

def get_cmip6_temp(start_date, end_date):
    # Process data month by month to reduce computation time
    start_year = int(start_date.split('-')[0])
    end_year = int(end_date.split('-')[0])
    
    all_data = []
    for year in range(start_year, end_year + 1):
        print(f"Processing CMIP6 data for year {year}...")
        
        # Process one month at a time
        for month in range(1, 13):
            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year}-12-31"
            else:
                end_date = f"{year}-{month+1:02d}-01"
            
            try:
                # Use SSP5-8.5 scenario for high-end projection
                # Limit to a few representative models to speed up computation
                cmip6_dataset = ee.ImageCollection('NASA/GDDP-CMIP6')\
                    .filterDate(start_date, end_date)\
                    .filter(ee.Filter.eq('scenario', 'ssp585'))\
                    .filter(ee.Filter.inList('model', ['ACCESS-CM2', 'MIROC6', 'MPI-ESM1-2-HR']))\
                    .select('tas')
                
                # First reduce the collection to a single image with maximum values
                max_image = cmip6_dataset.max()
                
                # Then get the maximum temperature for our point
                temp = max_image.reduceRegion(
                    reducer=ee.Reducer.max(),
                    geometry=RMMC_POINT,
                    scale=27830,
                    maxPixels=1e9
                ).get('tas')
                
                # Create a feature with the temperature
                feature = ee.Feature(None, {
                    'date': start_date,
                    'temperature': temp
                })
                
                temps = feature.getInfo()
                if temps and 'properties' in temps and 'temperature' in temps['properties']:
                    year_data = pd.DataFrame([{
                        'date': pd.to_datetime(temps['properties']['date']),
                        'temperature': temps['properties']['temperature'] - 273.15  # Convert K to °C
                    }])
                    all_data.append(year_data)
                    print(f"Successfully processed {year}-{month:02d}")
                else:
                    print(f"No data available for {year}-{month:02d}")
            except Exception as e:
                print(f"Error processing {year}-{month:02d}: {str(e)}")
                continue
    
    if not all_data:
        raise ValueError("No CMIP6 data could be processed")
        
    return pd.concat(all_data, ignore_index=True)

def analyze_heat_waves(df, reference_temp=None):
    """
    Analyze heat waves using SAWS definition: >5°C above average max for hottest part of year
    """
    # Calculate average maximum temperature for the hottest months (Dec-Feb)
    df['month'] = pd.to_datetime(df['date']).dt.month
    summer_months = df[df['month'].isin([12, 1, 2])]
    avg_summer_max = summer_months['temperature'].mean()
    
    # SAWS heatwave threshold: 5°C above average summer maximum
    heatwave_threshold = avg_summer_max + 5
    
    # Find days exceeding threshold
    hot_days = df['temperature'] > heatwave_threshold
    
    # Identify heat waves (3+ consecutive days above threshold)
    heat_wave_days = []
    current_streak = 0
    heat_waves = 0
    
    for hot in hot_days:
        if hot:
            current_streak += 1
            if current_streak >= 3:  # Count as part of heatwave if 3+ consecutive days
                heat_wave_days.append(True)
            else:
                heat_wave_days.append(False)
        else:
            if current_streak >= 3:  # End of a heatwave
                heat_waves += 1
            current_streak = 0
            heat_wave_days.append(False)
    
    # Add last heatwave if it ends at the end of the period
    if current_streak >= 3:
        heat_waves += 1
    
    # Calculate metrics
    total_heat_wave_days = sum(heat_wave_days)
    days_above_threshold = sum(hot_days)
    
    return {
        'mean_max_temp': df['temperature'].mean(),
        'max_temp': df['temperature'].max(),
        'threshold': heatwave_threshold,
        'days_above_threshold': days_above_threshold,
        'heatwave_days': total_heat_wave_days,
        'heatwaves_per_year': heat_waves,
        'avg_summer_max': avg_summer_max
    }

# Create output directory
output_dir = 'heatwave_analysis_warm_season'
os.makedirs(output_dir, exist_ok=True)

# Get and analyze historical data (1980-1989)
print("Analyzing historical period (1980-1989)...")
df_historical = get_era5_temp('1980-01-01', '1989-12-31')
historical_analysis = analyze_heat_waves(df_historical)

# Get and analyze current data (2015-2024)
print("Analyzing current period (2015-2024)...")
df_current = get_era5_temp('2015-01-01', '2024-12-31')
current_analysis = analyze_heat_waves(df_current)

# Create heat wave trend visualizations
plt.style.use('seaborn-v0_8')

# FT style settings
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['figure.titlesize'] = 12
plt.rcParams['figure.dpi'] = 300

# Common text elements
data_source = 'Data Source: ERA5 Historical & Current Temperature Data'
location = 'Location: Rahima Moosa Mother and Child Hospital (-26.1752°S, 28.0183°E)'
note = 'Note: Heat wave defined as 3+ consecutive days with temperatures >5°C above average summer maximum (SAWS definition)'
methodology = f'Methodology: Analysis based on daily maximum temperatures for spring and summer months (Sep-Feb)'

def add_source_and_notes(plt, additional_note=None):
    plt.figtext(0.1, 0.02, data_source, fontsize=8, alpha=0.7)
    plt.figtext(0.1, 0.04, location, fontsize=8, alpha=0.7)
    plt.figtext(0.1, 0.06, methodology, fontsize=8, alpha=0.7)
    if additional_note:
        plt.figtext(0.1, 0.08, additional_note, fontsize=8, alpha=0.7)
    plt.subplots_adjust(bottom=0.2)  # Adjust bottom margin for notes

# Define periods for historical and current only
periods = ['Historical\n(1980-1989)', 'Current\n(2015-2024)']

# 1. Heat Wave Days Bar Plot
plt.figure(figsize=(12, 8))
heatwave_days = [historical_analysis['heatwave_days'], 
                 current_analysis['heatwave_days']]

bars = plt.bar(periods, heatwave_days, color=['#0F5499', '#990F3D'])
plt.title('Heat Wave Days Show Dramatic Increase at Rahima Moosa Hospital', 
          pad=20, fontweight='bold')
plt.ylabel('Number of Heat Wave Days per Season')

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f}',
             ha='center', va='bottom',
             fontweight='bold')

# Add percentage increase
percent_increase = ((current_analysis['heatwave_days'] - historical_analysis['heatwave_days']) / 
                   historical_analysis['heatwave_days'] * 100)
plt.text(0.5, max(heatwave_days) * 0.6, 
         f'+{percent_increase:.0f}% increase\nfrom historical period',
         ha='center', va='center',
         fontweight='bold', color='#666666')

plt.grid(axis='y', linestyle='--', alpha=0.3)
add_source_and_notes(plt, note)
plt.savefig(os.path.join(output_dir, 'heatwave_days_comparison.png'), 
            dpi=300, bbox_inches='tight')
plt.close()

# 2. Heat Wave Frequency Plot
plt.figure(figsize=(12, 8))
heatwaves = [historical_analysis['heatwaves_per_year'], 
             current_analysis['heatwaves_per_year']]

bars = plt.bar(periods, heatwaves, color=['#0F5499', '#990F3D'])
plt.title('Frequency of Heat Waves Has More Than Doubled', 
          pad=20, fontweight='bold')
plt.ylabel('Number of Heat Waves per Season')

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f}',
             ha='center', va='bottom',
             fontweight='bold')

# Add percentage increase
percent_increase = ((current_analysis['heatwaves_per_year'] - historical_analysis['heatwaves_per_year']) / 
                   historical_analysis['heatwaves_per_year'] * 100)
plt.text(0.5, max(heatwaves) * 0.6, 
         f'+{percent_increase:.0f}% increase\nfrom historical period',
         ha='center', va='center',
         fontweight='bold', color='#666666')

plt.grid(axis='y', linestyle='--', alpha=0.3)
add_source_and_notes(plt, note)
plt.savefig(os.path.join(output_dir, 'heatwave_frequency_comparison.png'), 
            dpi=300, bbox_inches='tight')
plt.close()

# 3. Combined Metrics Plot
fig, ax1 = plt.subplots(figsize=(12, 8))

x = np.arange(len(periods))
width = 0.35

# Plot heat wave days
ax1.bar(x - width/2, heatwave_days, width, label='Heat Wave Days',
        color='#990F3D', alpha=0.8)
ax1.set_ylabel('Heat Wave Days per Season', color='#990F3D')
ax1.tick_params(axis='y', labelcolor='#990F3D')

# Create second y-axis for number of heat waves
ax2 = ax1.twinx()
ax2.bar(x + width/2, heatwaves, width, label='Number of Heat Waves',
        color='#0F5499', alpha=0.8)
ax2.set_ylabel('Number of Heat Waves per Season', color='#0F5499')
ax2.tick_params(axis='y', labelcolor='#0F5499')

# Set x-axis labels
plt.xticks(x, periods)

# Add title
plt.title('Heat Wave Days and Frequency Have Increased Substantially',
          pad=20, fontweight='bold')

# Add legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# Add value labels
for i, v in enumerate(heatwave_days):
    ax1.text(i - width/2, v, f'{v:.1f}', ha='center', va='bottom', color='#990F3D', fontweight='bold')
for i, v in enumerate(heatwaves):
    ax2.text(i + width/2, v, f'{v:.1f}', ha='center', va='bottom', color='#0F5499', fontweight='bold')

add_source_and_notes(plt, note)
plt.savefig(os.path.join(output_dir, 'heatwave_combined_metrics.png'),
            dpi=300, bbox_inches='tight')
plt.close()

# 4. Temperature Threshold Exceedance Plot
plt.figure(figsize=(12, 8))
days_above_90th = [historical_analysis['days_above_threshold'],
                   current_analysis['days_above_threshold']]

bars = plt.bar(periods, days_above_90th, color=['#0F5499', '#990F3D'])
plt.title('Days Above Historical Temperature Threshold\nHave Nearly Tripled',
          pad=20, fontweight='bold')
plt.ylabel('Number of Days Above Threshold')

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f}',
             ha='center', va='bottom',
             fontweight='bold')

# Add percentage increase
percent_increase = ((current_analysis['days_above_threshold'] - historical_analysis['days_above_threshold']) / 
                   historical_analysis['days_above_threshold'] * 100)
plt.text(0.5, max(days_above_90th) * 0.6, 
         f'+{percent_increase:.0f}% increase\nfrom historical period',
         ha='center', va='center',
         fontweight='bold', color='#666666')

plt.grid(axis='y', linestyle='--', alpha=0.3)
threshold_note = f"Note: Heat wave threshold is {historical_analysis['threshold']:.1f}°C\n(5°C above average summer maximum of {historical_analysis['avg_summer_max']:.1f}°C)"
add_source_and_notes(plt, threshold_note)
plt.savefig(os.path.join(output_dir, 'temperature_threshold_exceedance.png'),
            dpi=300, bbox_inches='tight')
plt.close()

print("\nVisualization files have been saved to:", output_dir)
print("1. heatwave_days_comparison.png - Shows the dramatic increase in heat wave days")
print("2. heatwave_frequency_comparison.png - Shows the increase in heat wave frequency")
print("3. heatwave_combined_metrics.png - Shows parallel trends in days and frequency")
print("4. temperature_threshold_exceedance.png - Shows increase in days above threshold")

print("\nHeat Wave Analysis for Rahima Moosa Mother and Child Hospital")
print("(Spring and Summer Months: September-February)")

print("\nHistorical Period (1980-1989):")
print(f"Mean maximum temperature: {historical_analysis['mean_max_temp']:.1f}°C")
print(f"Absolute maximum temperature: {historical_analysis['max_temp']:.1f}°C")
print(f"Days above 90th percentile per warm season: {historical_analysis['days_above_threshold']:.1f}")
print(f"Heat wave days per warm season: {historical_analysis['heatwave_days']:.1f}")
print(f"Number of heat waves per warm season: {historical_analysis['heatwaves_per_year']:.1f}")

print("\nCurrent Period (2015-2024):")
print(f"Mean maximum temperature: {current_analysis['mean_max_temp']:.1f}°C")
print(f"Absolute maximum temperature: {current_analysis['max_temp']:.1f}°C")
print(f"Days above 90th percentile per warm season: {current_analysis['days_above_threshold']:.1f}")
print(f"Heat wave days per warm season: {current_analysis['heatwave_days']:.1f}")
print(f"Number of heat waves per warm season: {current_analysis['heatwaves_per_year']:.1f}")

print(f"\nNote: Heat wave defined as 3+ consecutive days with temperatures >5°C above average summer maximum (SAWS definition)")
print(f"Historical spring/summer 90th percentile threshold: {historical_analysis['threshold']:.1f}°C")

# Save the data
df_historical.to_csv(os.path.join(output_dir, 'historical_temps_warm_season.csv'), index=False)
df_current.to_csv(os.path.join(output_dir, 'current_temps_warm_season.csv'), index=False)
