import ee
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.collections
import seaborn as sns
import numpy as np
from datetime import datetime
import matplotlib.patches as patches
from PIL import Image
import io
from tqdm import tqdm
import calendar
import sys
import pickle
import os
import imageio.v2 as imageio

# Set publication-ready style
plt.style.use('seaborn')
sns.set_palette("husl")
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

# Define Johannesburg coordinates (Rahima Moosa Hospital)
JOBURG_CENTER = ee.Geometry.Point([28.0183, -26.1752])
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

def load_cached_data(cache_file):
    """Load data from cache if available."""
    if os.path.exists(cache_file):
        print(f"Loading cached data from {cache_file}...")
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    return None

def save_to_cache(data, cache_file):
    """Save data to cache file."""
    print(f"Saving data to cache {cache_file}...")
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)

def create_frame(historical_dfs, current_df, projection_dfs, spring_summer_months, frame_number, temp_folder):
    """Create a single frame for the animation."""
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Colors for different periods - temperature progression from cool to hot
    historical_color = '#4575B4'  # Cool blue
    current_color = '#FF6B35'     # Warm orange
    projected_color = '#D73027'   # Hot red
    
    # Process data
    if isinstance(historical_dfs, dict) and historical_dfs:
        historical_seasonal = pd.concat([df[df['month'].isin(spring_summer_months)] 
                                       for df in historical_dfs.values()])
    else:
        historical_seasonal = historical_dfs[historical_dfs['month'].isin(spring_summer_months)]
    
    current_seasonal = current_df[current_df['month'].isin(spring_summer_months)]
    
    if isinstance(projection_dfs, dict) and projection_dfs:
        projected_seasonal = pd.concat([df[df['month'].isin(spring_summer_months)] 
                                      for df in projection_dfs.values()])
    else:
        projected_seasonal = projection_dfs[projection_dfs['month'].isin(spring_summer_months)]
    
    # Calculate means
    historical_mean = historical_seasonal['temperature'].mean()
    current_mean = current_seasonal['temperature'].mean()
    projected_mean = projected_seasonal['temperature'].mean()
    
    # Create title with better spacing
    title = 'Maximum Temperature Analysis for Johannesburg'
    subtitle = 'Historical (1980-1989) vs Current (2015-2024) vs Projected (2045-2055)'
    location = 'Location: Rahima Moosa Mother and Child Hospital (-26.1752°S, 28.0183°E)'
    
    fig.text(0.5, 0.98, title, fontsize=14, fontweight='bold', ha='center')
    fig.text(0.5, 0.935, subtitle, fontsize=12, ha='center')
    fig.text(0.5, 0.89, location, fontsize=10, ha='center', style='italic')
    
    # Progressive plotting based on frame number
    if frame_number >= 1:
        sns.kdeplot(y=historical_seasonal['temperature'], ax=ax, color=historical_color,
                    label=f'Historical (1980-1989) (Mean: {historical_mean:.1f}°C)',
                    fill=True, alpha=0.3)
    
    if frame_number >= 2:
        sns.kdeplot(y=current_seasonal['temperature'], ax=ax, color=current_color,
                    label=f'Current (2015-2024) (Mean: {current_mean:.1f}°C)',
                    fill=True, alpha=0.3)
        # Add first temperature change annotation
        temp_change_current = current_mean - historical_mean
        x_pos = ax.get_xlim()[1] * 0.85
        y_pos_current = (historical_mean + current_mean) / 2
        ax.text(x_pos, y_pos_current, f'+{temp_change_current:.1f}°C',
                color=current_color, ha='left', va='center', fontweight='bold')
    
    if frame_number >= 3:
        sns.kdeplot(y=projected_seasonal['temperature'], ax=ax, color=projected_color,
                    label=f'Projected (2045-2055) (Mean: {projected_mean:.1f}°C)',
                    fill=True, alpha=0.3)
        # Add second temperature change annotation
        temp_change_projected = projected_mean - current_mean
        y_pos_projected = (current_mean + projected_mean) / 2
        ax.text(x_pos, y_pos_projected, f'+{temp_change_projected:.1f}°C',
                color=projected_color, ha='left', va='center', fontweight='bold')
    
    # Customize axis
    ax.set_ylabel('Maximum Temperature (°C)')
    ax.set_xlabel('Frequency')
    ax.set_xticks([])
    ax.set_yticks(np.arange(25, 41, 1))
    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    
    # Update the legend order to match visual order (historical at bottom, projected at top)
    handles = [patches.Patch(color=projected_color), 
              patches.Patch(color=current_color),
              patches.Patch(color=historical_color)]
    labels = ['Projected', 'Current', 'Historical']
    ax.legend(handles, labels, loc='upper left')
    
    # Save frame
    plt.savefig(os.path.join(temp_folder, f'frame_{frame_number}.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_time_series_plot(historical_dfs, current_df, projection_dfs):
    """
    Create a time series plot showing temperature trends across historical, current, and projected periods.
    Shows only spring and summer months for consistency with the density plot.
    """
    plt.style.use('default')
    fig = plt.figure(figsize=(12, 8))
    
    # Define spring and summer months (September to February in Southern Hemisphere)
    spring_summer_months = [9, 10, 11, 12, 1, 2]
    
    # Process historical data
    if isinstance(historical_dfs, dict) and historical_dfs:
        historical_data = pd.concat(historical_dfs.values())
        historical_temps = historical_data[historical_data['month'].isin(spring_summer_months)]['temperature']
    else:
        historical_temps = historical_dfs[historical_dfs['month'].isin(spring_summer_months)]['temperature']
    
    # Process current data
    current_temps = current_df[current_df['month'].isin(spring_summer_months)]['temperature']
    
    # Process projection data
    if isinstance(projection_dfs, dict) and projection_dfs:
        projection_data = pd.concat(projection_dfs.values())
        projected_temps = projection_data[projection_data['month'].isin(spring_summer_months)]['temperature']
    else:
        projected_temps = projection_dfs[projection_dfs['month'].isin(spring_summer_months)]['temperature']
    
    # Create categories and combine data
    data = pd.DataFrame({
        'Period': ['Historical'] * len(historical_temps) + 
                 ['Current'] * len(current_temps) + 
                 ['Projected'] * len(projected_temps),
        'Temperature': pd.concat([historical_temps, current_temps, projected_temps])
    })
    
    # Calculate means for each period
    means = data.groupby('Period')['Temperature'].mean().reindex(['Historical', 'Current', 'Projected'])
    
    # Custom colors for mean line and points
    mean_color = '#E74C3C'   # Bright red for means
    
    # Create scatter plot with temperature-based colors
    for period_idx, period in enumerate(['Historical', 'Current', 'Projected']):
        period_data = data[data['Period'] == period]
        temperatures = period_data['Temperature']
        
        # Add small random jitter to x positions
        x_jittered = np.random.normal(period_idx, 0.1, size=len(temperatures))
        
        # Create scatter plot with temperature-based colors
        scatter = plt.scatter(x_jittered, temperatures, 
                            c=temperatures, cmap='RdYlBu_r',
                            alpha=0.6, s=30)
    
    # Plot means and connect them with a line
    plt.plot(range(3), means.values, 'o-', 
            color=mean_color, 
            markersize=12, linewidth=2.5,
            label='Mean Maximum Temperature',
            zorder=5)  # Ensure means are plotted on top
    
    # Add mean values as text annotations
    for i, mean in enumerate(means):
        plt.annotate(f'{mean:.1f}°C',
                    xy=(i, mean),
                    xytext=(0, 10), textcoords='offset points',
                    ha='center', va='bottom',
                    color=mean_color,
                    fontweight='bold')
    
    # Create title with better spacing
    title = 'Maximum Temperature Trends Across Time Periods\n(Spring & Summer Months)'
    subtitle = 'Historical (1980-1989) vs Current (2015-2024) vs Projected (2045-2055)'
    location = 'Location: Rahima Moosa Mother and Child Hospital (-26.1752°S, 28.0183°E)'
    data_source = 'Data Sources: ERA5 (Historical & Current), CMIP6 SSP5-8.5 (Projected)'
    
    # Add titles and labels
    plt.title(title + '\n' + subtitle + '\n' + location, 
             pad=20, fontsize=14, fontweight='bold')
    plt.xlabel('Time Period', fontsize=12, labelpad=10)
    plt.ylabel('Maximum Temperature (°C)', fontsize=12, labelpad=10)
    
    # Set x-axis ticks
    plt.xticks(range(3), ['Historical', 'Current', 'Projected'])
    
    # Add colorbar
    cbar = plt.colorbar(scatter)
    cbar.set_label('Maximum Temperature (°C)', fontsize=10)
    
    # Customize grid
    plt.grid(True, axis='y', linestyle='--', alpha=0.3)
    plt.gca().set_axisbelow(True)  # Put grid behind points
    
    # Customize spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_linewidth(0.5)
    plt.gca().spines['bottom'].set_linewidth(0.5)
    
    # Add legend
    plt.legend(['Mean Maximum Temperature'], 
              loc='upper left', 
              frameon=True, 
              framealpha=0.9,
              edgecolor='none')
    
    # Add data source at the bottom
    plt.figtext(0.02, -0.05, data_source, fontsize=10, style='italic')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig('temperature_trends.png', dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.close()

def create_animated_visualization(historical_dfs, current_df, projection_dfs):
    """Create an animated visualization showing progressive warming."""
    print("\nCreating animated visualization...")
    
    # Create temporary folder for frames
    temp_folder = 'temp_frames'
    os.makedirs(temp_folder, exist_ok=True)
    
    # Create frames
    spring_summer_months = [9, 10, 11, 12, 1, 2]
    for frame in range(1, 5):  # 4 frames: empty, historical, current, projected
        create_frame(historical_dfs, current_df, projection_dfs, 
                    spring_summer_months, frame, temp_folder)
    
    # Create GIF
    frames = []
    for frame in range(1, 5):
        frame_path = os.path.join(temp_folder, f'frame_{frame}.png')
        frames.append(imageio.imread(frame_path))
    
    # Save with much longer durations for each frame
    durations = [8.0, 8.0, 8.0, 12.0]  # Much longer durations: 8 seconds per transition, 12 seconds for final
    imageio.mimsave('temperature_analysis.gif', frames, duration=durations, loop=0)
    
    # Clean up temporary files
    for frame in range(1, 5):
        os.remove(os.path.join(temp_folder, f'frame_{frame}.png'))
    os.rmdir(temp_folder)
    
    print("Animation complete! Check 'temperature_analysis.gif' for results.")

if __name__ == "__main__":
    print("=== Analyzing Johannesburg Temperature Data ===")
    
    cache_file = 'temperature_data_cache.pkl'
    cached_data = load_cached_data(cache_file)
    
    if cached_data is None:
        # Fetch all data if not cached
        print("\nFetching Historical Data...")
        historical_dfs = {}
        historical_data = get_data_for_period(1980, 1989, JOBURG_AREA)
        if historical_data is not None:
            historical_dfs['1980-1989'] = historical_data
            
        print("\nFetching Current Data...")
        current_df = get_data_for_period(2015, 2024, JOBURG_AREA)
        
        print("\nFetching Future Projections...")
        projection_dfs = {}
        projection_data = get_data_for_period(2045, 2055, JOBURG_AREA, dataset='CMIP6', scenario='ssp585')
        if projection_data is not None:
            projection_dfs['2045-2055'] = projection_data
        
        # Save to cache
        cached_data = {
            'historical': historical_dfs,
            'current': current_df,
            'projected': projection_dfs
        }
        save_to_cache(cached_data, cache_file)
    else:
        historical_dfs = cached_data['historical']
        current_df = cached_data['current']
        projection_dfs = cached_data['projected']

    # Create the animated visualization
    create_animated_visualization(historical_dfs, current_df, projection_dfs)
    
    # Create the new time series plot
    create_time_series_plot(historical_dfs, current_df, projection_dfs)
    print("\nCreated time series plot: temperature_trends.png")
