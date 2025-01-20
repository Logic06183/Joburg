"""
Heat Wave Analysis Plan for Rahima Moosa Hospital
-----------------------------------------------
This script outlines and implements a comprehensive heat wave analysis using both
SAWS and 90th percentile definitions, focusing on spring and summer seasons.

Author: Craig Parker
Institution: Wits Planetary Health Research
Date: January 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import xarray as xr
import sys
import logging
from pathlib import Path
from data_retrieval import ERA5DataRetriever
from visualization import HeatWaveVisualizer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create output directories
Path('figures/heatwave_analysis').mkdir(parents=True, exist_ok=True)

# Constants and Configuration
LOCATION = {
    'name': 'Rahima_Moosa_Hospital',
    'latitude': -26.1752,
    'longitude': 28.0183
}

# Analysis periods
PERIODS = {
    'historical': {
        'start': '1980-01-01',
        'end': '1989-12-31',
        'description': 'Baseline historical climate before significant anthropogenic changes'
    },
    'current': {
        'start': '2015-01-01',
        'end': '2024-01-20',  # Using most recent available data
        'description': 'Present-day climate reflecting recent temperature patterns (up to most recent available data)'
    }
}

SEASONS = {
    'spring': [9, 10, 11],
    'summer': [12, 1, 2],
    'extended_warm': [11, 12, 1, 2, 3]
}

def get_era5_data(start_date, end_date):
    """
    Retrieve ERA5 daily maximum temperature data for the specified period.
    """
    # Implementation will use existing ERA5 data retrieval function
    pass

def calculate_heatwaves_saws(df, baseline_period=None):
    """
    Calculate heat waves using SAWS definition (>5°C above max average).
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Temperature data with 'date' and 'temperature' columns
    baseline_period : tuple, optional
        (start_date, end_date) for baseline period calculation
        
    Returns:
    --------
    dict
        Dictionary containing heat wave metrics
    """
    # Calculate baseline if provided, otherwise use the entire dataset
    if baseline_period:
        baseline_data = df[(df['date'] >= baseline_period[0]) & 
                          (df['date'] <= baseline_period[1])]
    else:
        baseline_data = df
        
    # Calculate summer maximum average
    summer_months = [12, 1, 2]
    summer_data = baseline_data[baseline_data['date'].dt.month.isin(summer_months)]
    summer_max_avg = summer_data['temperature'].mean()
    
    # SAWS threshold
    threshold = summer_max_avg + 5
    
    # Identify heat wave days and events
    hot_days = df['temperature'] > threshold
    
    # Calculate heat wave events (3+ consecutive days)
    events = []
    days_count = 0
    event_count = 0
    
    for hot in hot_days:
        if hot:
            days_count += 1
        else:
            if days_count >= 3:
                event_count += 1
                events.append(days_count)
            days_count = 0
            
    # Add last event if it ends at the end of the period
    if days_count >= 3:
        event_count += 1
        events.append(days_count)
        
    return {
        'threshold': threshold,
        'baseline_summer_max': summer_max_avg,
        'total_days': sum(events),
        'num_events': event_count,
        'event_lengths': events
    }

def calculate_heatwaves_percentile(df, baseline_period=None):
    """
    Calculate heat waves using 90th percentile definition (2+ consecutive days).
    """
    if baseline_period:
        baseline_data = df[(df['date'] >= baseline_period[0]) & 
                          (df['date'] <= baseline_period[1])]
    else:
        baseline_data = df
        
    # Calculate 90th percentile threshold
    threshold = baseline_data['temperature'].quantile(0.9)
    
    # Identify heat wave days and events
    hot_days = df['temperature'] > threshold
    
    # Calculate heat wave events (2+ consecutive days)
    events = []
    days_count = 0
    event_count = 0
    
    for hot in hot_days:
        if hot:
            days_count += 1
        else:
            if days_count >= 2:
                event_count += 1
                events.append(days_count)
            days_count = 0
            
    # Add last event if it ends at the end of the period
    if days_count >= 2:
        event_count += 1
        events.append(days_count)
        
    return {
        'threshold': threshold,
        'total_days': sum(events),
        'num_events': event_count,
        'event_lengths': events
    }

def analyze_seasonal_patterns(df, definition='saws'):
    """
    Analyze heat wave patterns by season.
    """
    results = {}
    
    for season_name, months in SEASONS.items():
        season_data = df[df['date'].dt.month.isin(months)].copy()
        
        if definition == 'saws':
            metrics = calculate_heatwaves_saws(season_data)
        else:
            metrics = calculate_heatwaves_percentile(season_data)
            
        results[season_name] = metrics
        
    return results

def create_visualizations(historical_data, current_data, historical_metrics, current_metrics):
    """
    Create comprehensive visualizations using FT styling.
    """
    from visualization import HeatWaveVisualizer
    
    # Initialize visualizer
    viz = HeatWaveVisualizer(output_dir='figures/heatwave_analysis')
    
    # Create SAWS definition comparisons
    viz.plot_heatwave_comparison(
        historical_metrics['saws'],
        current_metrics['saws'],
        metric='days',
        definition='SAWS'
    )
    
    viz.plot_heatwave_comparison(
        historical_metrics['saws'],
        current_metrics['saws'],
        metric='events',
        definition='SAWS'
    )
    
    # Create 90th percentile definition comparisons
    viz.plot_heatwave_comparison(
        historical_metrics['percentile'],
        current_metrics['percentile'],
        metric='days',
        definition='90th Percentile'
    )
    
    viz.plot_heatwave_comparison(
        historical_metrics['percentile'],
        current_metrics['percentile'],
        metric='events',
        definition='90th Percentile'
    )
    
    # Create temperature distribution plot
    viz.plot_temperature_distribution(historical_data, current_data)
    
    # Create interactive dashboard
    viz.create_interactive_dashboard(
        historical_data,
        current_data,
        {'historical': historical_metrics['saws'], 'current': current_metrics['saws']},
        {'historical': historical_metrics['percentile'], 'current': current_metrics['percentile']}
    )

def calculate_heatwave_metrics(data):
    """Calculate heat wave metrics from temperature data."""
    # Convert temperature from Kelvin to Celsius
    data = data.copy()  # Create a copy to avoid modifying the original
    data['temperature_celsius'] = data['temperature'] - 273.15
    
    # Calculate summer maximum average (Dec, Jan, Feb)
    summer_months = [12, 1, 2]
    summer_data = data[data['date'].dt.month.isin(summer_months)]
    summer_max_avg = summer_data['temperature_celsius'].mean()
    
    # SAWS threshold (5°C above summer maximum average)
    threshold = summer_max_avg + 5
    
    # Identify heat wave days
    data['is_heatwave'] = (data['temperature_celsius'] > threshold).astype(int)
    
    # Calculate consecutive days
    data['consec_days'] = (data['is_heatwave'] != data['is_heatwave'].shift()).cumsum()
    event_groups = data[data['is_heatwave'] == 1].groupby('consec_days')
    
    # Find events with 3+ consecutive days
    events = [len(group) for name, group in event_groups if len(group) >= 3]
    
    # Calculate metrics
    metrics = {
        'heat_wave_days': sum(events),
        'num_events': len(events),
        'avg_summer_max': summer_max_avg,
        'annual_events': len(events) / (data['date'].max().year - data['date'].min().year + 1)
    }
    
    return metrics, data

def analyze_periods():
    """Analyze and compare historical and current periods."""
    try:
        logging.info("Starting period comparison analysis...")
        
        # Initialize data retriever
        logging.info("Initializing ERA5 data retriever...")
        data_retriever = ERA5DataRetriever(LOCATION)
        
        try:
            # Historical period analysis
            logging.info("Analyzing historical period (1980-1989)...")
            historical_data = data_retriever.get_data_for_period('historical', PERIODS['historical'])
            logging.info(f"Historical data columns: {historical_data.columns.tolist()}")
            logging.info(f"Historical data head:\n{historical_data.head()}")
            
            # Current period analysis
            logging.info("Analyzing current period (2015-2024)...")
            current_data = data_retriever.get_data_for_period('current', PERIODS['current'])
            logging.info(f"Current data columns: {current_data.columns.tolist()}")
            logging.info(f"Current data head:\n{current_data.head()}")
            
            # Create visualizations
            logging.info("Creating visualizations...")
            try:
                visualizer = HeatWaveVisualizer()
                fig = visualizer.create_period_comparison(historical_data, current_data)
                logging.info("Visualization complete")
                return fig
            except Exception as viz_error:
                logging.error(f"Error in visualization: {str(viz_error)}")
                raise
                
        except Exception as data_error:
            logging.error(f"Error in data retrieval: {str(data_error)}")
            raise
            
    except Exception as e:
        logging.error(f"Error in analysis: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        analyze_periods()
    except Exception as e:
        logging.error(f"Main execution error: {str(e)}")
        raise
