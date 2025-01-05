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
import sys

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
            all_data = []
            years = list(range(start_year, end_year + 1))
            
            # Create progress bar for years
            with tqdm(years, desc=f"Processing CMIP6 {scenario} data") as pbar:
                for year in pbar:
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
                    
                    pbar.set_postfix({'temp': f"{temp_celsius:.1f}°C"})
            
            if all_data:
                df = pd.DataFrame(all_data)
                print(f"\nCMIP6 {scenario} data summary:")
                print(f"Max temperature: {df['temperature'].max():.1f}°C")
                print(f"Temperature range: {df['temperature'].min():.1f}°C to {df['temperature'].max():.1f}°C")
                return df
            return None
        except Exception as e:
            print(f"Error with CMIP6 data: {e}")
            return None

def get_data_for_period(start_year, end_year, aoi, dataset='ERA5', scenario=None):
    # Calculate total years for progress tracking
    total_years = end_year - start_year + 1
    chunk_size = 5  # Process 5 years at a time
    
    all_data = []
    chunks = [(i, min(i + chunk_size - 1, end_year)) 
              for i in range(start_year, end_year + 1, chunk_size)]
    
    with tqdm(chunks, desc=f"Fetching {dataset} data") as pbar:
        for chunk_start, chunk_end in pbar:
            df = get_temperature_data(chunk_start, chunk_end, aoi, dataset, scenario)
            if df is not None:
                all_data.append(df)
                if len(df) > 0:
                    pbar.set_postfix({'temp': f"{df['temperature'].max():.1f}°C"})
    
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        print(f"\n{dataset} data summary for {start_year}-{end_year}:")
        print(f"Records: {len(final_df)}")
        print(f"Temperature range: {final_df['temperature'].min():.1f}°C to {final_df['temperature'].max():.1f}°C")
        return final_df
    return None

def create_comparison_plot(historical_dfs, current_df, projection_dfs):
    """Create comparison plot for historical, current and projected temperatures."""
    print("\nCreating visualization...")
    
    # Set up the plot style
    plt.style.use('default')
    plt.rcParams.update({
        'figure.figsize': [12, 14],  # Adjusted for better aspect ratio
        'font.size': 12,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.dpi': 300
    })
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 14), height_ratios=[1, 1])
    fig.subplots_adjust(top=0.92, bottom=0.08, hspace=0.25)  # Adjusted spacing
    fig.suptitle('Temperature Analysis for Johannesburg\nHistorical (1979-1989) vs Current (2015-2024) vs Projected (2045-2055)', 
                 fontsize=14, fontweight='bold', y=0.95)
    
    # Colors for different periods
    historical_color = '#1f77b4'  # Blue
    current_color = '#2ca02c'     # Green
    projected_color = '#ff7f0e'   # Orange
    
    # Plot Spring/Summer (Sep-Feb)
    spring_summer_months = [9, 10, 11, 12, 1, 2]
    plot_seasonal_kde(ax1, historical_dfs, current_df, projection_dfs, spring_summer_months,
                     historical_color, current_color, projected_color)
    ax1.set_title('Spring/Summer Temperatures (Sep-Feb)', pad=10)
    
    # Plot Autumn/Winter (Mar-Aug)
    autumn_winter_months = [3, 4, 5, 6, 7, 8]
    plot_seasonal_kde(ax2, historical_dfs, current_df, projection_dfs, autumn_winter_months,
                     historical_color, current_color, projected_color)
    ax2.set_title('Autumn/Winter Temperatures (Mar-Aug)', pad=10)
    
    # Common settings for both subplots
    for ax in [ax1, ax2]:
        ax.set_xlabel('Maximum Temperature (°C)')
        ax.set_ylabel('Density')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='upper right', framealpha=0.9)
        
    # Add data source information
    fig.text(0.1, 0.02, 
             'Data sources: ERA5-Land monthly averaged data (Copernicus Climate Change Service)\n' +
             'Projections: CMIP6 Global Projections (Worst-case scenario SSP5-8.5)',
             fontsize=8, ha='left')
    
    plt.tight_layout()
    plt.savefig('temperature_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_seasonal_kde(ax, historical_dfs, current_df, projection_dfs, months,
                     historical_color, current_color, projected_color):
    """Plot seasonal data using KDE for a specific set of months."""
    
    # Filter and plot historical data
    historical_seasonal = pd.concat([df[df['month'].isin(months)] for df in historical_dfs.values()])
    historical_mean = historical_seasonal['temperature'].mean()
    
    # Plot historical KDE
    sns.kdeplot(data=historical_seasonal['temperature'], ax=ax, color=historical_color,
                label=f'Historical (1979-1989) (Mean: {historical_mean:.1f}°C)',
                linewidth=2)
    
    # Fill under historical KDE curve
    line = ax.lines[-1]
    x, y = line.get_data()
    ax.fill_between(x, 0, y, color=historical_color, alpha=0.2)
    
    # Filter and plot current data
    current_seasonal = current_df[current_df['month'].isin(months)]
    current_mean = current_seasonal['temperature'].mean()
    
    # Plot current KDE
    sns.kdeplot(data=current_seasonal['temperature'], ax=ax, color=current_color,
                label=f'Current (2015-2024) (Mean: {current_mean:.1f}°C)',
                linewidth=2)
    
    # Fill under current KDE curve
    line = ax.lines[-1]
    x, y = line.get_data()
    ax.fill_between(x, 0, y, color=current_color, alpha=0.2)
    
    # Filter and plot projection data
    projection_seasonal = pd.concat([df[df['month'].isin(months)] for df in projection_dfs.values()])
    projection_mean = projection_seasonal['temperature'].mean()
    
    # Plot projection KDE
    sns.kdeplot(data=projection_seasonal['temperature'], ax=ax, color=projected_color,
                label=f'Projected (2045-2055) (Mean: {projection_mean:.1f}°C)',
                linewidth=2)
    
    # Fill under projection KDE curve
    line = ax.lines[-1]
    x, y = line.get_data()
    ax.fill_between(x, 0, y, color=projected_color, alpha=0.2)
    
    # Add temperature change annotations
    y_pos = ax.get_ylim()[1] * 0.8
    ax.annotate(f'+{current_mean - historical_mean:.1f}°C',
                xy=(historical_mean + 1, y_pos),
                xytext=(current_mean - 1, y_pos),
                arrowprops=dict(arrowstyle='<->', color='gray'),
                ha='center', va='bottom', fontsize=10)
    
    ax.annotate(f'+{projection_mean - current_mean:.1f}°C',
                xy=(current_mean + 1, y_pos),
                xytext=(projection_mean - 1, y_pos),
                arrowprops=dict(arrowstyle='<->', color='gray'),
                ha='center', va='bottom', fontsize=10)

if __name__ == "__main__":
    print("=== Analyzing Johannesburg Temperature Data ===")
    
    # Historical data (1979-1989)
    print("\nFetching Historical Data...")
    historical_dfs = {}
    historical_data = get_data_for_period(1979, 1989, JOBURG_AREA, 'ERA5')
    if historical_data is not None:
        historical_dfs['1979-1989'] = historical_data
    
    # Current data (2015-2024)
    print("\nFetching Current Data...")
    current_df = get_data_for_period(2015, 2024, JOBURG_AREA, 'ERA5')
    
    # Future projections (2045-2055)
    print("\nFetching Future Projections...")
    projection_dfs = {}
    projection_data = get_data_for_period(2045, 2055, JOBURG_AREA, 'CMIP6', scenario='ssp585')
    if projection_data is not None:
        projection_dfs['2045-2055 (SSP5-8.5)'] = projection_data
    
    # Create the plot if we have data
    if current_df is not None:
        print("\nCreating visualization...")
        create_comparison_plot(historical_dfs, current_df, projection_dfs)
        print("Analysis complete! Check 'temperature_analysis.png' for results.")
