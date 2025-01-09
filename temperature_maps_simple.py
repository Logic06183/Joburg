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

# Define Johannesburg coordinates (Rahima Moosa Hospital)
HOSPITAL_LAT = -26.1752
HOSPITAL_LON = 28.0183
JOBURG_CENTER = ee.Geometry.Point([HOSPITAL_LON, HOSPITAL_LAT])
BUFFER_DISTANCE = 5000  # 5km buffer
JOBURG_AREA = JOBURG_CENTER.buffer(BUFFER_DISTANCE)

def get_landsat_collection(start_year, end_year, months=[9,10,11,12,1,2]):
    """Get Landsat collection for the specified time period."""
    # Use Landsat 8 for recent/future and Landsat 5 for historical
    if start_year >= 2013:
        collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        thermal_band = 'ST_B10'
    else:
        collection = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
        thermal_band = 'ST_B6'
    
    # Filter by date and area
    filtered = collection.filterBounds(JOBURG_AREA) \
        .filter(ee.Filter.calendarRange(start_year, end_year, 'year')) \
        .filter(ee.Filter.calendarRange(months[0], months[-1], 'month'))
    
    return filtered, thermal_band

def create_map():
    """Create a simple map for visualization."""
    map_obj = geemap.Map(
        center=[HOSPITAL_LAT, HOSPITAL_LON],
        zoom=13,
    )
    return map_obj

def main():
    print("Creating temperature map for Johannesburg...")
    
    # Create base map
    m = create_map()
    
    # Get current period data
    collection, thermal_band = get_landsat_collection(2015, 2024)
    
    # Calculate mean temperature
    mean_temp = collection.select(thermal_band).mean()
    
    # Add the temperature layer to the map
    vis_params = {
        'min': 290,
        'max': 320,
        'palette': ['blue', 'cyan', 'green', 'yellow', 'red']
    }
    
    m.addLayer(mean_temp, vis_params, 'Land Surface Temperature')
    m.addLayerControl()
    
    # Save the map
    output_file = 'temperature_map_simple.html'
    m.save(output_file)
    print(f"Map saved as {output_file}")
    return output_file

if __name__ == "__main__":
    output_file = main()
    print(f"\nTo view the map, open {output_file} in your web browser.")
