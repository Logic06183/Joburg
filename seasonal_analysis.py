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

def get_temperature_data(start_year, end_year, aoi, dataset='ERA5', scenario=None):
    if dataset == 'ERA5':
        def get_monthly_temp(start_date, end_date):
            try:
                dataset = ee.ImageCollection('ECMWF/ERA5/MONTHLY')\
                    .filter(ee.Filter.date(start_date, end_date))\
                    .select('mean_2m_air_temperature')
                
                def process_image(image):
                    date = ee.Date(image.get('system:time_start'))
                    month = date.get('month')
                    year = date.get('year')
                    
                    temp = image.reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=aoi,
                        scale=30000
                    ).get('mean_2m_air_temperature')
                    
                    temp_celsius = ee.Number(temp).subtract(273.15)
                    
                    return ee.Feature(None, {
                        'temperature': temp_celsius,
                        'month': month,
                        'year': year
                    })
                
                features = dataset.map(process_image)
                return features.getInfo()
            except Exception as e:
                print(f"Error fetching ERA5 data for {start_date} to {end_date}: {e}")
                return None
    
    elif dataset == 'CMIP6':
        def get_monthly_temp(start_date, end_date):
            try:
                # Get daily data and aggregate to monthly
                dataset = ee.ImageCollection('NASA/GDDP-CMIP6')\
                    .filter(ee.Filter.date(start_date, end_date))\
                    .filter(ee.Filter.eq('scenario', scenario))\
                    .filter(ee.Filter.eq('model', 'EC-Earth3'))\
                    .select('tas')
                
                # Function to get month and year from an image
                def get_month_year(image):
                    date = ee.Date(image.get('system:time_start'))
                    return ee.Feature(None, {
                        'month': date.get('month'),
                        'year': date.get('year')
                    })
                
                # Get unique month-year combinations
                dates = dataset.map(get_month_year).distinct(['month', 'year']).limit(500)
                
                def process_monthly_temp(feature):
                    month = feature.get('month')
                    year = feature.get('year')
                    
                    # Filter images for this month and year
                    monthly_images = dataset.filter(
                        ee.Filter.And(
                            ee.Filter.eq('month', month),
                            ee.Filter.eq('year', year)
                        )
                    )
                    
                    # Calculate monthly mean
                    monthly_mean = monthly_images.mean()
                    
                    temp = monthly_mean.reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=aoi,
                        scale=30000
                    ).get('tas')
                    
                    temp_celsius = ee.Number(temp).subtract(273.15)
                    
                    return ee.Feature(None, {
                        'temperature': temp_celsius,
                        'month': month,
                        'year': year
                    })
                
                features = dates.map(process_monthly_temp)
                return features.getInfo()
            except Exception as e:
                print(f"Error fetching CMIP6 data for {start_date} to {end_date}: {e}")
                return None

    print(f"Fetching {dataset} data for {start_year}-{end_year}...")
    data = get_monthly_temp(f'{start_year}-01-01', f'{end_year}-12-31')
    
    if data is None or 'features' not in data or not data['features']:
        print(f"No data returned for {dataset} {start_year}-{end_year}")
        return None
        
    try:
        features_list = []
        for feature in data['features']:
            props = feature['properties']
            if all(key in props for key in ['temperature', 'month', 'year']):
                try:
                    temp = float(props['temperature'])
                    month = int(props['month'])
                    year = int(props['year'])
                    if -100 <= temp <= 100 and 1 <= month <= 12:  # Basic validation
                        features_list.append({
                            'year': year,
                            'month': month,
                            'temperature': temp
                        })
                except (ValueError, TypeError) as e:
                    print(f"Error processing feature: {e}")
                    continue
        
        if not features_list:
            print(f"No valid features found for {dataset} {start_year}-{end_year}")
            return None
            
        df = pd.DataFrame(features_list)
        
        if scenario:
            df['scenario'] = scenario
        
        print(f"Successfully processed {dataset} data for {start_year}-{end_year}")
        print(f"Data shape: {df.shape}, Columns: {df.columns.tolist()}")
        print(f"Temperature range: {df['temperature'].min():.1f}°C to {df['temperature'].max():.1f}°C")
        return df
    
    except Exception as e:
        print(f"Error processing {dataset} data for {start_year}-{end_year}: {e}")
        return None

def plot_frame(historical_dfs, current_df, projection_dfs, frame_number, total_frames):
    # Create figure with fixed size and DPI
    dpi = 100
    fig = plt.figure(figsize=(12, 14), dpi=dpi)
    gs = plt.GridSpec(2, 1, height_ratios=[1, 1], hspace=0.3)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    
    # Color schemes and labels
    periods = {
        '1979-1989': {'color': '#1f78b4', 'style': '-'},
        '1990-2000': {'color': '#a6cee3', 'style': '-'},
        '2015-2024': {'color': '#33a02c', 'style': '-'},
        '2045-2055 (SSP2-4.5)': {'color': '#fb9a99', 'style': '--'},
        '2045-2055 (SSP5-8.5)': {'color': '#e31a1c', 'style': '--'}
    }
    
    seasons = {
        'Spring': {'months': [9, 10, 11], 'ax': ax1, 'title': 'Spring (September-November)'},
        'Summer': {'months': [12, 1, 2], 'ax': ax2, 'title': 'Summer (December-February)'}
    }
    
    # Calculate transition factor (0 to 1)
    transition = frame_number / total_frames
    
    for season_name, season_info in seasons.items():
        ax = season_info['ax']
        months = season_info['months']
        
        # Plot with transition effect
        periods_to_plot = []
        if transition < 0.25:  # Show historical data first
            alpha = min(1, transition * 4)
            if '1979-1989' in historical_dfs:
                periods_to_plot.append(('1979-1989', historical_dfs['1979-1989'], alpha))
        elif transition < 0.5:  # Add 1990-2000
            alpha = min(1, (transition - 0.25) * 4)
            if '1979-1989' in historical_dfs:
                periods_to_plot.append(('1979-1989', historical_dfs['1979-1989'], 1))
            if '1990-2000' in historical_dfs:
                periods_to_plot.append(('1990-2000', historical_dfs['1990-2000'], alpha))
        elif transition < 0.75:  # Add current period
            alpha = min(1, (transition - 0.5) * 4)
            for period, df in historical_dfs.items():
                periods_to_plot.append((period, df, 1))
            periods_to_plot.append(('2015-2024', current_df, alpha))
        else:  # Add projections
            alpha = min(1, (transition - 0.75) * 4)
            for period, df in historical_dfs.items():
                periods_to_plot.append((period, df, 1))
            periods_to_plot.append(('2015-2024', current_df, 1))
            for scenario, df in projection_dfs.items():
                periods_to_plot.append((scenario, df, alpha))
        
        for period, df, alpha in periods_to_plot:
            data = df[df['month'].isin(months)]['temperature']
            mean_temp = data.mean()
            sns.kdeplot(data=data, ax=ax, color=periods[period]['color'],
                       fill=True, alpha=alpha * 0.3, 
                       label=f'{period} (Mean: {mean_temp:.1f}°C)')
        
        # Set fixed axis limits for consistent frame sizes
        ax.set_xlim(5, 30)
        ax.set_ylim(0, 0.5)
        
        # Customize the plot
        ax.set_title(season_info['title'], pad=20, fontsize=12, fontweight='bold')
        ax.set_xlabel('Temperature (°C)', fontsize=11)
        ax.set_ylabel('Density', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        ax.set_yticks([])
    
    # Add data source information
    source_text = (
        "Data sources:\n"
        "Historical & Current: ERA5 monthly averaged data on single levels from 1979 to present (Copernicus Climate Change Service)\n"
        "Projections: NASA Earth Exchange Global Daily Downscaled Projections (NEX-GDDP-CMIP6)"
    )
    
    # Create a white box for the source text
    source_bbox = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8)
    plt.figtext(0.05, 0.02, source_text, fontsize=8, bbox=source_bbox)
    
    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=dpi)
    plt.close()
    
    # Convert to PIL Image
    buf.seek(0)
    return Image.open(buf)

def create_temperature_animation(historical_dfs, current_df, projection_dfs):
    print("\nCreating animation frames...")
    n_frames = 60  # Total number of frames for smooth animation
    
    # Create frames
    frames = []
    for i in tqdm(range(n_frames)):
        img = plot_frame(historical_dfs, current_df, projection_dfs, i, n_frames-1)
        # Convert to RGB mode and resize to fixed dimensions
        img = img.convert('RGB')
        img = img.resize((1200, 1400), Image.Resampling.LANCZOS)
        frames.append(img)
    
    print("\nSaving GIF animation...")
    # Save the animation with a longer duration for the final frame
    durations = [100] * (n_frames - 1) + [2000]  # 100ms per frame, 2s for last frame
    frames[0].save(
        'temperature_evolution.gif',
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0
    )
    
    print("Animation saved as 'temperature_evolution.gif'")

if __name__ == "__main__":
    print("Fetching data from Google Earth Engine...")
    
    print("\nSetting up data retrieval...")
    
    # Define your area of interest (Johannesburg)
    aoi = ee.Geometry.Point([28.0473, -26.2041])
    
    # Get historical data
    historical_dfs = {
        '1979-1989': get_temperature_data(1979, 1989, aoi),
        '1990-2000': get_temperature_data(1990, 2000, aoi)
    }
    
    # Get current data
    current_df = get_temperature_data(2015, 2024, aoi)
    
    # Get projection data
    projection_dfs = {
        '2045-2055 (SSP2-4.5)': get_temperature_data(2045, 2055, aoi, dataset='CMIP6', scenario='ssp245'),
        '2045-2055 (SSP5-8.5)': get_temperature_data(2045, 2055, aoi, dataset='CMIP6', scenario='ssp585')
    }
    
    # Create the animation
    create_temperature_animation(historical_dfs, current_df, projection_dfs)
