import ee
import geemap
import numpy as np
from datetime import datetime
import os
from PIL import Image
import io

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
    return image.addBands(lst.rename('LST'))

def create_lst_map(start_year, end_year):
    """Create a map showing LST for the specified period."""
    Map = geemap.Map(center=[HOSPITAL_LAT, HOSPITAL_LON], zoom=13)
    
    # Add only Esri World Imagery basemap
    Map.add_basemap('HYBRID')
    
    # Get data
    collection, thermal_band, mult, add = get_landsat_collection(start_year, end_year)
    processed = collection.map(lambda img: calculate_lst(img, thermal_band, mult, add))
    mean_lst = processed.select('LST').mean()
    
    # Add LST layer with transparency
    Map.addLayer(
        mean_lst, 
        LST_VIS_PARAMS,
        f'LST ({start_year}-{end_year})'
    )
    
    # Add hospital marker with label
    hospital = ee.Geometry.Point([HOSPITAL_LON, HOSPITAL_LAT])
    Map.addLayer(hospital, {'color': 'white'}, 'Rahima Moosa Hospital')
    
    # Add a text label for the hospital
    Map.add_text(
        text='Rahima Moosa Hospital',
        xy=(HOSPITAL_LON, HOSPITAL_LAT),
        font_size=12,
        font_color='white',
        font_family='arial',
        anchor='left'
    )
    
    # Add colorbar
    Map.add_colorbar(
        vis_params=LST_VIS_PARAMS,
        label='Land Surface Temperature (°C)',
        orientation='horizontal',
        transparent_bg=True
    )
    
    return Map

def create_animation():
    """Create an animated GIF of LST changes over time."""
    periods = [
        (1990, 1999),
        (2000, 2009),
        (2014, 2023)
    ]
    
    frames = []
    print("Generating maps for each period...")
    
    for start_year, end_year in periods:
        print(f"Processing {start_year}-{end_year}...")
        Map = create_lst_map(start_year, end_year)
        
        # Save map as PNG
        temp_file = f'temp_map_{start_year}_{end_year}.png'
        Map.save(temp_file)
        
        # Open the image and append to frames
        with Image.open(temp_file) as img:
            frames.append(img.copy())
        
        # Clean up temporary file
        os.remove(temp_file)
    
    # Save the animation
    output_file = 'lst_animation.gif'
    print(f"\nSaving animation to {output_file}...")
    
    # Save the first frame
    frames[0].save(
        output_file,
        save_all=True,
        append_images=frames[1:],
        duration=2000,  # 2 seconds per frame
        loop=0
    )
    
    print("Animation created successfully!")

if __name__ == "__main__":
    print("=== Creating LST Animation for Johannesburg ===")
    create_animation()
