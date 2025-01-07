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
    'min': 28,  # Adjusted minimum temperature
    'max': 42,  # Adjusted maximum temperature
    'palette': [
        '#313695',  # Deep blue (coolest)
        '#74add1',  # Light blue
        '#fee090',  # Light yellow
        '#fdae61',  # Light orange
        '#f46d43',  # Orange
        '#d73027',  # Red
        '#a50026'   # Deep red (hottest)
    ],
    'opacity': 0.8  # Increased opacity
}

def get_landsat_collection(start_year, end_year):
    """Get Landsat collection for peak summer months (Dec-Feb)."""
    if start_year >= 2013:
        collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        thermal_band = 'ST_B10'
    else:
        collection = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
        thermal_band = 'ST_B6'
    
    mult = 0.00341802
    add = 149.0
    
    # Filter for summer months only (December, January, February)
    filtered = collection.filterBounds(JOBURG_AREA) \
        .filter(ee.Filter.calendarRange(start_year, end_year, 'year')) \
        .filter(ee.Filter.calendarRange(12, 2, 'month'))  # Peak summer months
    
    return filtered, thermal_band, mult, add

def calculate_lst(image, thermal_band, mult, add):
    """Calculate Land Surface Temperature in Celsius."""
    lst = image.select(thermal_band).multiply(mult).add(add).subtract(273.15)
    return lst.rename('LST')

def create_lst_map(start_year, end_year, title):
    """Create a map showing LST for the specified period."""
    Map = geemap.Map(center=[HOSPITAL_LAT, HOSPITAL_LON], zoom=13)
    Map.add_basemap('HYBRID')
    
    # Get data
    collection, thermal_band, mult, add = get_landsat_collection(start_year, end_year)
    lst = collection.map(lambda img: calculate_lst(img, thermal_band, mult, add))
    
    # Calculate percentile values instead of mean
    lst_p90 = lst.reduce(ee.Reducer.percentile([90]))  # Use 90th percentile for hot days
    
    # Add LST layer with transparency
    Map.addLayer(
        lst_p90, 
        LST_VIS_PARAMS,
        f'Peak Summer LST ({start_year}-{end_year})'
    )
    
    # Add a point for the hospital location
    hospital_point = ee.Geometry.Point([HOSPITAL_LON, HOSPITAL_LAT])
    Map.addLayer(
        ee.FeatureCollection([ee.Feature(hospital_point)]),
        {'color': 'red', 'pointSize': 10},
        'Hospital Location'
    )
    
    # Add a prominent text label for the hospital
    Map.add_text(
        text=f"Rahima Moosa Hospital\nPeak Summer LST {start_year}-{end_year}",
        xy=(HOSPITAL_LON, HOSPITAL_LAT + 0.002),  # Offset label slightly
        font_size=20,
        font_color='white',
        font_family='arial',
        font_weight='bold',
        background_color='rgba(0,0,0,0.8)',
        padding=(8, 8)
    )
    
    # Add a legend
    Map.add_legend(
        title="Peak Summer Land Surface Temperature",
        legend_dict={
            'Cool (28°C)': '#313695',
            'Moderate': '#74add1',
            'Warm': '#fee090',
            'Hot': '#fdae61',
            'Very Hot': '#f46d43',
            'Extreme': '#d73027',
            'Very Extreme (42°C)': '#a50026'
        }
    )
    
    return Map

def create_all_maps():
    """Create maps for different periods."""
    periods = [
        (1980, 1995, 'Early Period'),
        (1995, 2010, 'Mid Period'),
        (2010, 2023, 'Recent Period')
    ]
    
    for start_year, end_year, label in periods:
        print(f"\nProcessing {label} ({start_year}-{end_year})...")
        Map = create_lst_map(start_year, end_year, label)
        
        # Save the map
        output_file = f'lst_map_{start_year}_{end_year}.html'
        Map.save(output_file)
        print(f"Map saved to {output_file}")

if __name__ == "__main__":
    print("=== Creating Peak Summer LST Maps for Johannesburg ===")
    create_all_maps()
    print("\nAll maps created! Open the HTML files in your browser to view them.")
