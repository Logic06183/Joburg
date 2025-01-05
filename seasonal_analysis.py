import ee
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import matplotlib.patches as patches
from PIL import Image
import io
from tqdm import tqdm
import calendar

# Set publication-ready style
plt.style.use('seaborn-v0_8-paper')
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['figure.titlesize'] = 12
plt.rcParams['figure.dpi'] = 300

# Initialize Earth Engine with authentication
try:
    ee.Initialize()
except Exception as e:
    print("Error initializing Earth Engine. Please authenticate first.")
    print("Run 'earthengine authenticate' in your terminal.")
    raise e

print("Fetching data from Google Earth Engine...")

# Define Johannesburg coordinates (City Center)
JOBURG_CENTER = ee.Geometry.Point([28.0473, -26.2041])
JOBURG_AREA = JOBURG_CENTER.buffer(5000)  # 5km buffer is enough for city center

def get_temperature_data(start_year, end_year, aoi, dataset='ERA5', scenario=None):
    if dataset == 'ERA5':
        try:
            # Use ERA5 monthly data for speed
            collection = ee.ImageCollection('ECMWF/ERA5/MONTHLY')\
                .filter(ee.Filter.date(f'{start_year}-01-01', f'{end_year}-12-31'))\
                .select('maximum_2m_air_temperature')
            
            def process_image(image):
                date = ee.Date(image.get('system:time_start'))
                temp = image.reduceRegion(
                    reducer=ee.Reducer.max(),
                    geometry=aoi,
                    scale=5000  # 5km resolution is enough for city-level analysis
                ).get('maximum_2m_air_temperature')
                
                return ee.Feature(None, {
                    'temperature': ee.Number(temp).subtract(273.15),  # Convert to Celsius
                    'month': date.get('month'),
                    'year': date.get('year')
                })
            
            features = collection.map(process_image).getInfo()
            
            if features and 'features' in features:
                data = []
                for f in features['features']:
                    if 'properties' in f:
                        data.append(f['properties'])
                
                df = pd.DataFrame(data)
                if not df.empty:
                    print(f"\nERA5 data for {start_year}-{end_year}")
                    print(f"Max temperature: {df['temperature'].max():.1f}°C")
                    print(f"Temperature range: {df['temperature'].min():.1f}°C to {df['temperature'].max():.1f}°C")
                    return df
            return None
        except Exception as e:
            print(f"Error with ERA5 data: {e}")
            return None
    
    elif dataset == 'CMIP6':
        try:
            # Use CMIP6 data with simplified processing - one year at a time
            all_data = []
            
            for year in range(start_year, end_year + 1):
                collection = ee.ImageCollection('NASA/GDDP-CMIP6')\
                    .filter(ee.Filter.date(f'{year}-01-01', f'{year}-12-31'))\
                    .filter(ee.Filter.eq('scenario', scenario))\
                    .select('tas')
                
                # Get monthly maximums
                for month in range(1, 13):
                    monthly_data = collection.filter(
                        ee.Filter.calendarRange(month, month, 'month')
                    )
                    
                    if monthly_data.size().getInfo() > 0:
                        max_temp = monthly_data.max()
                        temp = max_temp.reduceRegion(
                            reducer=ee.Reducer.max(),
                            geometry=aoi,
                            scale=5000
                        ).get('tas')
                        
                        temp_celsius = ee.Number(temp).subtract(273.15).getInfo()
                        all_data.append({
                            'year': year,
                            'month': month,
                            'temperature': temp_celsius
                        })
                
                print(f"Processed CMIP6 data for year {year}")
            
            if all_data:
                df = pd.DataFrame(all_data)
                print(f"\nCMIP6 {scenario} data for {start_year}-{end_year}")
                print(f"Max temperature: {df['temperature'].max():.1f}°C")
                print(f"Temperature range: {df['temperature'].min():.1f}°C to {df['temperature'].max():.1f}°C")
                return df
            return None
        except Exception as e:
            print(f"Error with CMIP6 data: {e}")
            return None

def get_data_for_period(start_year, end_year, aoi, dataset='ERA5', scenario=None):
    print(f"\nFetching {dataset} data for {start_year}-{end_year}...")
    
    # Get data in smaller chunks if period is long
    if end_year - start_year > 5:
        mid_year = start_year + (end_year - start_year) // 2
        df1 = get_temperature_data(start_year, mid_year, aoi, dataset, scenario)
        df2 = get_temperature_data(mid_year + 1, end_year, aoi, dataset, scenario)
        if df1 is not None and df2 is not None:
            return pd.concat([df1, df2])
        return df1 if df1 is not None else df2
    
    return get_temperature_data(start_year, end_year, aoi, dataset, scenario)

def create_comparison_plot(historical_dfs, current_df, projection_dfs):
    seasons = {
        'Spring': list(range(9, 12)),  # September to November
        'Summer': [12, 1, 2]  # December to February
    }
    
    fig, axes = plt.subplots(2, 1, figsize=(10, 12))
    fig.suptitle('Maximum Temperature Change in Johannesburg\nWarming Faster Than Global Average', y=0.95)
    
    for idx, (season, months) in enumerate(seasons.items()):
        ax = axes[idx]
        
        # Filter data for the current season and get maximum temperatures
        hist_season = pd.concat([df[df['month'].isin(months)]['temperature'] for df in historical_dfs.values()])
        curr_season = current_df[current_df['month'].isin(months)]['temperature']
        proj_season = pd.concat([df[df['month'].isin(months)]['temperature'] for df in projection_dfs.values()])
        
        # Calculate means of maximum temperatures
        hist_max_mean = hist_season.mean()
        curr_max_mean = curr_season.mean()
        proj_max_mean = proj_season.mean()
        
        # Plot density curves with higher temperature range
        sns.kdeplot(data=hist_season, ax=ax, color='lightblue', alpha=0.6, 
                   label=f'Pre-warming (1979-1989) (Mean Max: {hist_max_mean:.1f}°C)')
        sns.kdeplot(data=curr_season, ax=ax, color='lightgreen', alpha=0.6, 
                   label=f'Current (2015-2024) (Mean Max: {curr_max_mean:.1f}°C)')
        sns.kdeplot(data=proj_season, ax=ax, color='bisque', alpha=0.6, 
                   label=f'Projected (2045-2055) (Mean Max: {proj_max_mean:.1f}°C)')
        
        # Add arrows and temperature change annotations
        curr_change = curr_max_mean - hist_max_mean
        proj_change = proj_max_mean - curr_max_mean
        arrow_y = ax.get_ylim()[1] * 0.8
        
        # First arrow (historical to current)
        ax.annotate(f'+{curr_change:.1f}°C', 
                   xy=(hist_max_mean, arrow_y),
                   xytext=(curr_max_mean, arrow_y),
                   arrowprops=dict(arrowstyle='<->', color='blue', lw=1),
                   ha='center', va='bottom')
        
        # Second arrow (current to projected)
        ax.annotate(f'+{proj_change:.1f}°C',
                   xy=(curr_max_mean, arrow_y),
                   xytext=(proj_max_mean, arrow_y),
                   arrowprops=dict(arrowstyle='<->', color='red', lw=1),
                   ha='center', va='bottom')
        
        ax.set_title(f'{season} ({calendar.month_name[months[0]].capitalize()}-{calendar.month_name[months[-1]].capitalize()})')
        ax.set_xlabel('Maximum Temperature (°C)')
        ax.set_ylabel('Density')
        ax.legend()
        
        # Set x-axis range to focus on high temperatures
        if season == 'Spring':
            ax.set_xlim(15, 40)  # Adjusted for spring maximum temperatures
        else:  # Summer
            ax.set_xlim(20, 45)  # Adjusted for summer maximum temperatures
    
    # Add data source information
    plt.figtext(0.1, 0.02, 
                'Data sources: ERA5-Land monthly averaged data (Copernicus Climate Change Service)\n' +
                'Projections: CMIP6 Global Projections (Worst-case scenario SSP5-8.5)',
                fontsize=8, ha='left')
    
    plt.tight_layout()
    plt.savefig('temperature_distributions.png', 
                bbox_inches='tight',
                dpi=300,
                facecolor='white',
                edgecolor='none')
    plt.close()
    
    print("Plot saved as 'temperature_distributions.png'")

if __name__ == "__main__":
    print("=== Testing with smaller date ranges first ===")
    
    # Test with just 2 years of historical data
    print("\nTesting Historical Data (1979-1980)...")
    historical_dfs = {}
    historical_data = get_data_for_period(1979, 1980, JOBURG_AREA, 'ERA5')
    if historical_data is not None:
        historical_dfs['1979-1980'] = historical_data
        print(" Historical data retrieved successfully")
    
    # Test with 2 years of current data
    print("\nTesting Current Data (2022-2023)...")
    current_df = get_data_for_period(2022, 2023, JOBURG_AREA, 'ERA5')
    if current_df is not None:
        print(" Current data retrieved successfully")
    
    # Test with 2 years of projection data
    print("\nTesting Projection Data (2045-2046)...")
    projection_dfs = {}
    projection_data = get_data_for_period(2045, 2046, JOBURG_AREA, 'CMIP6', scenario='ssp585')
    if projection_data is not None:
        projection_dfs['2045-2046 (SSP5-8.5)'] = projection_data
        print(" Projection data retrieved successfully")
    
    # Create the plot if we have data
    if current_df is not None:
        print("\nCreating plot...")
        create_comparison_plot(historical_dfs, current_df, projection_dfs)
        print(" Done!")
