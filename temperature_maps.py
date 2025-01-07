import ee
import geemap
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from branca.colormap import LinearColormap
import os
import pickle
from tqdm import tqdm
import pandas as pd

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
        mult = 0.00341802
        add = 149.0
    else:
        collection = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
        thermal_band = 'ST_B6'
        mult = 0.00341802
        add = 149.0
    
    # Filter by date and area
    filtered = collection.filterBounds(JOBURG_AREA) \
        .filter(ee.Filter.calendarRange(start_year, end_year, 'year')) \
        .filter(ee.Filter.calendarRange(months[0], months[-1], 'month'))
    
    return filtered, thermal_band, mult, add

def calculate_lst(image, thermal_band, mult, add):
    """Calculate Land Surface Temperature."""
    # Convert thermal band to celsius
    lst = image.select(thermal_band).multiply(mult).add(add).subtract(273.15)
    return image.addBands(lst.rename('LST'))

def calculate_ndvi(image):
    """Calculate NDVI."""
    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    return image.addBands(ndvi)

def create_map():
    """Create a base map with the right settings."""
    m = geemap.Map(
        center=[HOSPITAL_LAT, HOSPITAL_LON],
        zoom=13,
        add_google_map=False
    )
    m.add_basemap('HYBRID')
    return m

def create_temperature_maps():
    """Create interactive maps with multiple Earth Engine layers."""
    print("Creating interactive maps with Earth Engine layers...")
    
    # Define time periods
    periods = [
        (1980, 1989, 'Historical (1980-1989)', 'map1'),
        (2015, 2024, 'Current (2015-2024)', 'map2'),
        (2045, 2055, 'Projected (2045-2055)', 'map3')
    ]
    
    maps = []
    print("\nProcessing Earth Engine data for each period...")
    
    for start_year, end_year, title, div_id in tqdm(periods):
        # Create map
        Map = create_map()
        
        try:
            # Get Landsat collection
            collection, thermal_band, mult, add = get_landsat_collection(start_year, end_year)
            
            # Calculate LST and NDVI
            processed = collection.map(lambda img: calculate_lst(img, thermal_band, mult, add)) \
                                .map(calculate_ndvi)
            
            # Calculate mean LST and NDVI
            mean_lst = processed.select('LST').mean()
            mean_ndvi = processed.select('NDVI').mean()
            
            # Add LST layer
            vis_params_lst = {
                'min': 25,
                'max': 35,
                'palette': ['blue', 'yellow', 'red']
            }
            Map.addLayer(mean_lst, vis_params_lst, 'Land Surface Temperature')
            
            # Add NDVI layer
            vis_params_ndvi = {
                'min': -1,
                'max': 1,
                'palette': ['red', 'yellow', 'green']
            }
            Map.addLayer(mean_ndvi, vis_params_ndvi, 'NDVI')
            
            # Add the area circle
            circle = ee.Geometry.Point([HOSPITAL_LON, HOSPITAL_LAT]).buffer(BUFFER_DISTANCE)
            Map.addLayer(circle, {'color': 'red'}, '5km Buffer')
            
            # Add a point for the hospital
            hospital = ee.Geometry.Point([HOSPITAL_LON, HOSPITAL_LAT])
            Map.addLayer(hospital, {'color': 'red'}, 'Rahima Moosa Hospital')
            
            # Add layer control
            Map.add_layer_control()
            
        except Exception as e:
            print(f"Error processing period {start_year}-{end_year}: {str(e)}")
            continue
        
        maps.append((Map, div_id))
    
    if not maps:
        print("No maps were successfully created.")
        return
    
    # Create HTML template
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Temperature Patterns - Rahima Moosa Hospital</title>
        <style>
            body {{ 
                margin: 0; 
                padding: 20px; 
                font-family: Arial, sans-serif; 
                background-color: #f5f5f5; 
            }}
            .map-container {{ 
                display: flex; 
                justify-content: space-between; 
                margin-bottom: 20px; 
                flex-wrap: wrap; 
            }}
            .map-wrapper {{ 
                width: 32%; 
                min-width: 400px; 
                margin-bottom: 20px; 
                background: white; 
                padding: 15px; 
                border-radius: 8px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
            }}
            .map {{ 
                width: 100%; 
                height: 500px; 
                border-radius: 4px; 
            }}
            h2 {{ 
                text-align: center; 
                margin: 10px 0; 
                color: #333; 
                font-size: 1.2em; 
            }}
            .title {{ 
                text-align: center; 
                margin-bottom: 30px; 
            }}
            .title h1 {{ 
                color: #2c3e50; 
                margin-bottom: 10px; 
            }}
            .title p {{ 
                color: #666; 
                margin-top: 0; 
            }}
            .legend {{ 
                margin-top: 10px; 
                text-align: center; 
                font-size: 0.9em; 
                color: #666; 
            }}
        </style>
    </head>
    <body>
        <div class="title">
            <h1>Temperature and Environmental Patterns Around Rahima Moosa Hospital</h1>
            <p>Interactive visualization of Land Surface Temperature (LST), Vegetation Index (NDVI), and other heat stress indicators</p>
        </div>
        <div class="map-container">
            <div class="map-wrapper">
                <h2>Historical (1980-1989)</h2>
                <div id="map1" class="map"></div>
                <div class="legend">Use the layer control to toggle between LST and NDVI</div>
            </div>
            <div class="map-wrapper">
                <h2>Current (2015-2024)</h2>
                <div id="map2" class="map"></div>
                <div class="legend">Use the layer control to toggle between LST and NDVI</div>
            </div>
            <div class="map-wrapper">
                <h2>Projected (2045-2055)</h2>
                <div id="map3" class="map"></div>
                <div class="legend">Use the layer control to toggle between LST and NDVI</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save maps
    print("\nSaving maps...")
    output_file = 'temperature_maps.html'
    
    with open(output_file, 'w') as f:
        f.write(html_content)
        
        for Map, div_id in maps:
            map_html = Map.to_html()
            script = f"""
            <script>
                document.getElementById('{div_id}').innerHTML = `{map_html}`;
            </script>
            """
            f.write(script)
    
    print(f"Maps saved! Open {output_file} in a web browser to view the interactive maps.")

if __name__ == "__main__":
    print("=== Creating Interactive Environmental Maps for Johannesburg ===")
    create_temperature_maps()
