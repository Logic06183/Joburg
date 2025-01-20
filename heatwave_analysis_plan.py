"""
Heat Wave Analysis Plan for Rahima Moosa Hospital
-----------------------------------------------
This script outlines and implements a comprehensive heat wave analysis using both
SAWS and 90th percentile definitions, focusing on spring and summer seasons.

Author: Craig Parker
Institution: Wits Planetary Health Research
Date: January 2025
"""

from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
from dataclasses import dataclass, field
from data_retrieval import DataConfig, TemperatureDataRetriever
from visualization import HeatWaveVisualizer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create output directories
Path('figures/heatwave_analysis').mkdir(parents=True, exist_ok=True)

@dataclass
class AnalysisConfig:
    """Configuration for heat wave analysis."""
    data_config: DataConfig
    analysis_periods: Dict[str, Tuple[int, int]] = field(default_factory=lambda: {
        'historical': (1980, 1989),
        'current': (2015, 2024)
    })

class HeatWaveAnalyzer:
    """Analyzes heat wave trends using multiple definitions."""
    
    def __init__(self, config: AnalysisConfig):
        """Initialize with configuration."""
        self.config = config
        self.data_retriever = TemperatureDataRetriever(config.data_config)
    
    def identify_heatwaves(self, data: pd.DataFrame) -> pd.DataFrame:
        """Identify heat wave days based on temperature threshold.
        
        A heat wave is defined as 3 or more consecutive days where the maximum 
        temperature exceeds the 90th percentile threshold (calculated from the 
        historical period 1980-1989).
        """
        # Calculate 90th percentile threshold
        threshold = np.percentile(data['temperature_celsius'], 90)
        
        # Mark days above threshold
        data['above_threshold'] = data['temperature_celsius'] > threshold
        data['is_heatwave'] = False
        
        # Find consecutive days (3 or more)
        consecutive_days = []
        current_streak = []
        
        for i, row in data.iterrows():
            if row['above_threshold']:
                current_streak.append(i)
                if len(current_streak) >= 3:
                    consecutive_days.extend(current_streak)
            else:
                current_streak = []
        
        # Mark heat wave days
        if consecutive_days:
            data.loc[consecutive_days, 'is_heatwave'] = True
        
        return data
    
    def analyze_period(self, data: pd.DataFrame) -> pd.DataFrame:
        """Analyze heat waves for a specific period."""
        # Filter for spring and summer months (Sep-Feb)
        data = data[data['date'].dt.month.isin([9, 10, 11, 12, 1, 2])].copy()
        
        # Identify heat waves
        data = self.identify_heatwaves(data)
        
        return data
    
    def analyze_trends(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Analyze heat wave trends for historical and current periods."""
        # Get data
        data = self.data_retriever.get_data()
        
        # Split into historical and current periods
        historical_data = data[
            (data['date'].dt.year >= self.config.analysis_periods['historical'][0]) &
            (data['date'].dt.year <= self.config.analysis_periods['historical'][1])
        ].copy()
        
        current_data = data[
            (data['date'].dt.year >= self.config.analysis_periods['current'][0]) &
            (data['date'].dt.year <= self.config.analysis_periods['current'][1])
        ].copy()
        
        # Analyze each period
        historical_data = self.analyze_period(historical_data)
        current_data = self.analyze_period(current_data)
        
        return historical_data, current_data

def main():
    """Main function to run heat wave analysis."""
    try:
        # Initialize configuration
        data_config = DataConfig()
        analysis_config = AnalysisConfig(data_config=data_config)
        
        # Create analyzer and visualizer
        analyzer = HeatWaveAnalyzer(analysis_config)
        visualizer = HeatWaveVisualizer()
        
        # Run analysis
        historical_data, current_data = analyzer.analyze_trends()
        
        # Create visualization
        visualizer.create_analysis_dashboard(historical_data, current_data)
        
        # Log results
        logging.info("Analysis completed successfully")
        
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        raise

if __name__ == "__main__":
    main()
