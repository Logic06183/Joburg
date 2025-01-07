import ee
import geemap
import numpy as np
from datetime import datetime

# Initialize Earth Engine
try:
    ee.Initialize()
except Exception as e:
    print("Error initializing Earth Engine. Please authenticate first.")
    print("Run 'earthengine authenticate' in your terminal.")
    raise e

# Define constants
HOSPITAL_LAT = -26.1752
HOSPITAL_LON = 28.0183
JOBURG_CENTER = ee.Geometry.Point([HOSPITAL_LON, HOSPITAL_LAT])
BUFFER_DISTANCE = 5000  # 5km buffer
JOBURG_AREA = JOBURG_CENTER.buffer(BUFFER_DISTANCE)

# Define visualization parameters for LST with transparency
LST_VIS_PARAMS = {
    'min': 22,
    'max': 38,
    'palette': [
        '#313695',  # Deep blue (coldest)
        '#74add1',  # Light blue
        '#fed976',  # Light orange
        '#fd8d3c',  # Orange
        '#f03b20',  # Red-orange
        '#bd0026'   # Deep red (hottest)
    ],
    'opacity': 0.5  # Set transparency to 50%
}

def get_landsat_collection(start_year, end_year, months=[9,10,11,12,1,2]):
    """Get Landsat collection for the specified time period."""
    if start_year >= 2013:
        collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        thermal_band = 'ST_B10'
    else:
        collection = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
        thermal_band = 'ST_B6'
    
    mult = 0.00341802
    add = 149.0
    
    filtered = collection.filterBounds(JOBURG_AREA) \
        .filter(ee.Filter.calendarRange(start_year, end_year, 'year')) \
        .filter(ee.Filter.calendarRange(months[0], months[-1], 'month'))
    
    return filtered, thermal_band, mult, add

def calculate_lst(image, thermal_band, mult, add):
    """Calculate Land Surface Temperature in Celsius."""
    lst = image.select(thermal_band).multiply(mult).add(add).subtract(273.15)
    return lst.rename('LST')

def create_lst_animation():
    """Create an interactive map with time-series animation."""
    # Create a map centered on the hospital
    Map = geemap.Map(center=[HOSPITAL_LAT, HOSPITAL_LON], zoom=13)
    Map.add_basemap('HYBRID')
    
    # Define time periods
    periods = [
        (1990, 1999, 'Early Period'),
        (2000, 2009, 'Mid Period'),
        (2014, 2023, 'Recent Period')
    ]
    
    # Create a list to store LST images
    lst_images = []
    
    # Process each period
    for start_year, end_year, label in periods:
        print(f"Processing {label} ({start_year}-{end_year})...")
        
        # Get and process Landsat data
        collection, thermal_band, mult, add = get_landsat_collection(start_year, end_year)
        lst = collection.map(lambda img: calculate_lst(img, thermal_band, mult, add))
        mean_lst = lst.mean()
        
        # Add label and timestamp
        labeled_lst = mean_lst.set({
            'system:time_start': ee.Date.fromYMD(start_year, 1, 1).millis(),
            'label': f'{start_year}-{end_year}'
        })
        
        lst_images.append(labeled_lst)
    
    # Convert list to image collection
    lst_collection = ee.ImageCollection.fromImages(lst_images)
    
    # Add the time-series animation
    Map.add_time_slider(
        lst_collection,
        LST_VIS_PARAMS,
        label='Land Surface Temperature (°C)',
        time_interval=3,  # 3 seconds per frame
        position='bottomright'
    )
    
    # Add a prominent text label for the hospital
    Map.add_text(
        text="Rahima Moosa Hospital",
        xy=(HOSPITAL_LON, HOSPITAL_LAT),
        font_size=16,
        font_color='white',
        font_family='arial',
        font_weight='bold',
        background_color='rgba(0,0,0,0.7)',
        padding=(5, 5)
    )
    
    # Add a legend
    Map.add_legend(
        title="Land Surface Temperature",
        legend_dict={
            'Cold (22°C)': '#313695',
            'Cool': '#74add1',
            'Moderate': '#fed976',
            'Warm': '#fd8d3c',
            'Hot': '#f03b20',
            'Very Hot (38°C)': '#bd0026'
        }
    )
    
    return Map

if __name__ == "__main__":
    print("=== Creating Interactive LST Animation for Johannesburg ===")
    Map = create_lst_animation()
    
    # Save the map
    output_file = 'lst_animation.html'
    Map.save(output_file)
    print(f"\nAnimation saved to {output_file}")
    
    # Display the map (when running in a notebook)
    try:
        display(Map)
    except:
        print(f"Please open {output_file} in a web browser using the serve_map.py script")
