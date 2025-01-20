"""
ERA5 Data Retrieval Module with Caching
-------------------------------------
Handles efficient retrieval and caching of ERA5 temperature data using GeoMap.

Author: Craig Parker
Institution: Wits Planetary Health Research
Date: January 2025
"""

import os
import pickle
import geemap
import ee
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants for Caching
CACHE_DIR = Path('./data_cache')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class ERA5DataRetriever:
    """
    Handles ERA5 data retrieval with caching functionality.
    """
    
    def __init__(self, location, cache_dir=CACHE_DIR):
        """
        Initialize the data retriever.
        
        Parameters:
        -----------
        location : dict
            Dictionary containing 'name', 'latitude', and 'longitude'
        cache_dir : Path
            Directory for caching data
        """
        self.location = location
        self.cache_dir = Path(cache_dir)
        
        # Initialize Earth Engine
        try:
            ee.Initialize()
            logger.info("Earth Engine initialized successfully")
        except Exception as e:
            logger.warning(f"Earth Engine initialization failed: {str(e)}")
            logger.info("Attempting to authenticate...")
            try:
                ee.Authenticate()
                ee.Initialize()
                logger.info("Authentication and initialization successful")
            except Exception as auth_e:
                logger.error(f"Authentication failed: {str(auth_e)}")
                raise
        
        self.point = ee.Geometry.Point([location['longitude'], location['latitude']])
    
    def _get_cache_filename(self, start_date, end_date):
        """Generate a unique cache filename."""
        safe_name = self.location['name'].replace(' ', '_')
        return self.cache_dir / f"era5_{safe_name}_{start_date}_{end_date}.pkl"
    
    def _load_cache(self, filename):
        """Load data from cache file."""
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
            logger.info(f"Successfully loaded cached data from {filename}")
            return data
        except Exception as e:
            logger.error(f"Error loading cache file {filename}: {str(e)}")
            raise
    
    def _save_cache(self, data, filename):
        """Save data to cache file."""
        try:
            with open(filename, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"Successfully saved data to cache file {filename}")
        except Exception as e:
            logger.error(f"Error saving to cache file {filename}: {str(e)}")
            raise
    
    def _get_yearly_chunks(self, start_date, end_date):
        """Split date range into yearly chunks."""
        start_year = pd.to_datetime(start_date).year
        end_year = pd.to_datetime(end_date).year
        chunks = []
        
        for year in range(start_year, end_year + 1):
            chunk_start = max(pd.to_datetime(f"{year}-01-01"), pd.to_datetime(start_date))
            chunk_end = min(pd.to_datetime(f"{year}-12-31"), pd.to_datetime(end_date))
            chunks.append((chunk_start.strftime('%Y-%m-%d'), chunk_end.strftime('%Y-%m-%d')))
        
        return chunks

    def get_era5_data(self, start_date, end_date):
        """
        Retrieve ERA5 data with caching.
        
        Parameters:
        -----------
        start_date : str
            Start date in YYYY-MM-DD format
        end_date : str
            End date in YYYY-MM-DD format
            
        Returns:
        --------
        pandas.DataFrame
            DataFrame containing date and temperature data
        """
        # Check for data availability (ERA5 typically has 2-3 months lag)
        current_date = pd.Timestamp.now()
        latest_available = current_date - pd.DateOffset(months=3)
        requested_end = pd.to_datetime(end_date)
        
        if requested_end > latest_available:
            logger.warning(f"ERA5 data typically has a 2-3 month lag. Data after {latest_available.strftime('%Y-%m-%d')} may not be available.")
            end_date = latest_available.strftime('%Y-%m-%d')
        
        cache_file = self._get_cache_filename(start_date, end_date)
        
        # Return cached data if available
        if cache_file.exists():
            logger.info(f"Found cached data for period {start_date} to {end_date}")
            df = self._load_cache(cache_file)
            return self._validate_and_format_data(df)
        
        logger.info(f"Fetching ERA5 data for period {start_date} to {end_date}")
        
        try:
            # Split into yearly chunks
            chunks = self._get_yearly_chunks(start_date, end_date)
            all_data = []
            
            for chunk_start, chunk_end in chunks:
                chunk_end_date = pd.to_datetime(chunk_end)
                if chunk_end_date > latest_available:
                    logger.info(f"Skipping future data chunk: {chunk_start} to {chunk_end}")
                    continue
                    
                logger.info(f"Processing chunk: {chunk_start} to {chunk_end}")
                
                # Load ERA5 data from Earth Engine for this chunk
                dataset = ee.ImageCollection("ECMWF/ERA5/DAILY") \
                    .filterDate(chunk_start, chunk_end) \
                    .select('maximum_2m_air_temperature')
                
                # Create a function to extract values at our point
                def extract_at_point(image):
                    value = image.reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=self.point,
                        scale=1000
                    ).get('maximum_2m_air_temperature')
                    
                    return ee.Feature(None, {
                        'date': image.date().format('YYYY-MM-dd'),
                        'temperature': value
                    })
                
                # Map over the collection
                features = dataset.map(extract_at_point)
                
                # Get the data
                data_list = features.getInfo()['features']
                
                if not data_list:
                    logger.warning(f"No data received for chunk {chunk_start} to {chunk_end}")
                    continue
                
                # Convert to DataFrame with consistent column naming
                temperature_data = [
                    {
                        'date': feature['properties']['date'],
                        'temperature_celsius': feature['properties']['temperature'] - 273.15  # Convert Kelvin to Celsius
                    }
                    for feature in data_list
                ]
                
                chunk_df = pd.DataFrame(temperature_data)
                chunk_df['date'] = pd.to_datetime(chunk_df['date'])
                all_data.append(chunk_df)
            
            if not all_data:
                raise ValueError("No data received from Earth Engine for any chunk")
            
            # Combine all chunks and validate
            df = pd.concat(all_data, ignore_index=True)
            df = df.sort_values('date').reset_index(drop=True)
            
            # Validate and format data
            df = self._validate_and_format_data(df)
            
            # Cache the complete dataset
            self._save_cache(df, cache_file)
            
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving ERA5 data: {str(e)}")
            raise

    def _validate_and_format_data(self, df):
        """Validate and format DataFrame to ensure consistent structure."""
        logger.debug("Validating and formatting data")
        
        # Ensure required columns exist
        required_columns = ['date', 'temperature_celsius']
        missing_cols = [col for col in required_columns if col not in df.columns]
        
        # Try to fix common column naming issues
        if 'temperature' in df.columns and 'temperature_celsius' in missing_cols:
            logger.debug("Renaming 'temperature' to 'temperature_celsius'")
            df = df.rename(columns={'temperature': 'temperature_celsius'})
            missing_cols.remove('temperature_celsius')
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            logger.debug("Converting date column to datetime")
            df['date'] = pd.to_datetime(df['date'])
        
        # Ensure temperature is float
        if not pd.api.types.is_float_dtype(df['temperature_celsius']):
            logger.debug("Converting temperature to float")
            df['temperature_celsius'] = df['temperature_celsius'].astype(float)
        
        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)
        
        logger.debug("Data validation and formatting complete")
        return df

    def get_data_for_period(self, period_name, period_dates):
        """
        Retrieve data for a specific named period.
        
        Parameters:
        -----------
        period_name : str
            Name of the period (e.g., 'historical', 'current')
        period_dates : dict
            Dictionary containing 'start' and 'end' dates
            
        Returns:
        --------
        pandas.DataFrame
            DataFrame containing the period's temperature data
        """
        logger.info(f"Retrieving data for {period_name} period")
        return self.get_era5_data(
            period_dates['start'],
            period_dates['end']
        )

def main():
    """
    Test the ERA5DataRetriever class.
    """
    # Test location
    location = {
        'name': 'Rahima_Moosa_Hospital',
        'latitude': -26.1752,
        'longitude': 28.0183
    }
    
    # Initialize retriever
    retriever = ERA5DataRetriever(location)
    
    # Test retrieval for a short period
    test_data = retriever.get_era5_data('2020-01-01', '2020-01-31')
    print("\nSample of retrieved data:")
    print(test_data.head())

if __name__ == "__main__":
    main()
