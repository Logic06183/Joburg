"""
Visualization Module for Heat Wave Analysis
----------------------------------------
Provides FT-styled visualizations for heat wave analysis results.

Author: Craig Parker
Institution: Wits Planetary Health Research
Date: January 2025
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import gaussian_kde
from PIL import ImageColor
import datetime
import logging
import time
import os
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FT Style Constants
FT_COLORS = {
    'background': '#FFF1E5',
    'main_red': '#990F3D',
    'light_red': '#FF8D8D',
    'dark_grey': '#333333',
    'mid_grey': '#666666',
    'axis_grey': '#CCC1B7'
}

FT_STYLE = {
    'font_family': 'MetricWeb, sans-serif',
    'title_size': 16,
    'axis_title_size': 12,
    'tick_size': 10,
    'annotation_size': 10,
    'grid_color': '#CCC1B7',
    'grid_alpha': 0.3
}

@dataclass
class PlotConfig:
    """Configuration for plot styling and colors."""
    colors: Dict[str, str] = field(default_factory=lambda: {
        'historical': '#2E5A87',  # Darker blue
        'current': '#E63946',     # Warm red
        'grid': '#CCCCCC',
        'annotation': '#666666'
    })
    
    fonts: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'title': {'size': 20, 'weight': 'bold'},
        'subtitle': {'size': 14},
        'axis': {'size': 12},
        'annotation': {'size': 10}
    })
    
    layout: Dict[str, Any] = field(default_factory=lambda: {
        'grid_opacity': 0.2,
        'spacing': {'vertical': 0.15, 'horizontal': 0.12},
        'margin': {'t': 100, 'b': 80, 'l': 50, 'r': 50}  # Using plotly margin keys
    })

class HeatWaveVisualizer:
    """Creates visualizations for heat wave analysis."""
    
    def __init__(self):
        """Initialize visualizer."""
        self.output_dir = Path('figures/heatwave_analysis')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.colors = {
            'historical': '#4C72B0',  # Darker blue
            'current': '#55A868'      # Muted green
        }
    
    def create_analysis_dashboard(self, historical_data: pd.DataFrame, current_data: pd.DataFrame) -> None:
        """Create a comprehensive dashboard comparing historical and current periods."""
        # Create figure with subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Temperature Distribution',
                'Heat Wave Events per Year',
                'Monthly Heat Wave Days',
                'Heat Wave Events per Season'
            ),
            specs=[[{}, {}],
                  [{}, {}],
                  [{"colspan": 2}, None]],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )

        # Add title
        fig.update_layout(
            title_text='Spring & Summer Heat Wave Trends at Rahima Moosa Hospital<br>Comparing Historical (1980-1989) vs Current (2015-2024) Periods',
            title_x=0.5,
            height=1200,
            showlegend=True,
            template='seaborn'
        )

        # Plot temperature distribution
        self._add_temperature_distribution(fig, historical_data, current_data, row=1, col=1)
        
        # Plot heat wave events per year
        self._add_heatwave_events(fig, historical_data, current_data, row=1, col=2)
        
        # Plot monthly heat wave days
        self._add_monthly_heatwaves(fig, historical_data, current_data, row=2, col=1)
        
        # Plot seasonal distribution
        self._add_seasonal_distribution(fig, historical_data, current_data, row=2, col=2)

        # Add findings and sources section
        findings_text = """
        <b>Key Findings:</b><br>
        1. Heat Wave Definition: A heat wave is defined as 3 or more consecutive days where the maximum temperature exceeds the 90th percentile threshold (calculated from the historical period 1980-1989).<br>
        2. Temperature Increase: The current period (2015-2024) shows a clear shift towards higher temperatures compared to the historical period (1980-1989).<br>
        3. Heat Wave Frequency: The frequency of heat wave events has increased in the current period, particularly during summer months.<br>
        4. Seasonal Patterns: Heat waves are most frequent in December, with February showing the highest average number of heat wave days.<br>
        <br>
        <b>Sources:</b><br>
        - Temperature Data: ERA5 reanalysis dataset (Hersbach et al., 2020)<br>
        - Heat Wave Definition: Based on WMO Guidelines for Heat Wave Definition (WMO, 2018)<br>
        - Analysis Period: Spring-Summer months (September-February) for both historical (1980-1989) and current (2015-2024) periods
        """
        
        fig.add_annotation(
            text=findings_text,
            xref="paper", yref="paper",
            x=0, y=-0.2,
            showarrow=False,
            font=dict(size=12),
            align="left",
            xanchor="left",
            yanchor="top"
        )

        # Update layout for the findings section
        fig.update_layout(
            margin=dict(t=100, b=300)  # Increase bottom margin for findings
        )

        # Save the figure
        timestamp = int(time.time())
        output_file = f'figures/heatwave_analysis/heatwave_analysis_{timestamp}.html'
        fig.write_html(output_file)
    
    def _add_temperature_distribution(self, fig, historical_data, current_data, row, col):
        """Add temperature distribution subplot."""
        # Create temperature bins
        bins = np.linspace(10, 35, 50)
        
        # Historical distribution
        hist_hist, _ = np.histogram(historical_data['temperature_celsius'], bins=bins, density=True)
        fig.add_trace(
            go.Bar(
                x=bins[:-1],
                y=hist_hist,
                name='1980-1989',
                marker_color=self.colors['historical'],
                opacity=0.7
            ),
            row=row, col=col
        )
        
        # Current distribution
        current_hist, _ = np.histogram(current_data['temperature_celsius'], bins=bins, density=True)
        fig.add_trace(
            go.Bar(
                x=bins[:-1],
                y=current_hist,
                name='2015-2024',
                marker_color=self.colors['current'],
                opacity=0.7
            ),
            row=row, col=col
        )
        
        fig.update_xaxes(title_text='Maximum Temperature (°C)', row=row, col=col)
        fig.update_yaxes(title_text='Proportion of Days', row=row, col=col)
    
    def _add_monthly_heatwaves(self, fig, historical_data, current_data, row, col):
        """Add monthly heat wave days subplot."""
        # Calculate monthly averages for both periods
        historical_monthly = historical_data.groupby(
            historical_data['date'].dt.month)['is_heatwave'].mean()
        current_monthly = current_data.groupby(
            current_data['date'].dt.month)['is_heatwave'].mean()
        
        # Define month order (Sep-Feb)
        month_order = [9, 10, 11, 12, 1, 2]
        month_names = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb']
        
        # Reorder data
        historical_monthly = historical_monthly.reindex(month_order)
        current_monthly = current_monthly.reindex(month_order)
        
        # Create traces
        fig.add_trace(
            go.Bar(
                x=month_names,
                y=historical_monthly,
                name='1980-1989',
                marker_color=self.colors['historical']
            ),
            row=row, col=col
        )
        
        fig.add_trace(
            go.Bar(
                x=month_names,
                y=current_monthly,
                name='2015-2024',
                marker_color=self.colors['current']
            ),
            row=row, col=col
        )
        
        fig.update_xaxes(title_text='Month', row=row, col=col)
        fig.update_yaxes(title_text='Average Heat Wave Days', row=row, col=col)
    
    def _add_annual_distribution(self, fig, historical_data, current_data, row, col):
        """Add annual heat wave distribution subplot."""
        # Calculate annual events
        historical_annual = historical_data.groupby(
            historical_data['date'].dt.year)['is_heatwave'].sum()
        current_annual = current_data.groupby(
            current_data['date'].dt.year)['is_heatwave'].sum()
        
        fig.add_trace(
            go.Box(
                y=historical_annual,
                name='1980-1989',
                marker_color=self.colors['historical'],
                boxpoints='all'
            ),
            row=row, col=col
        )
        
        fig.add_trace(
            go.Box(
                y=current_annual,
                name='2015-2024',
                marker_color=self.colors['current'],
                boxpoints='all'
            ),
            row=row, col=col
        )
        
        fig.update_xaxes(title_text='Period', row=row, col=col)
        fig.update_yaxes(title_text='Heat Wave Events per Season', row=row, col=col)
    
    def _add_heatwave_events(self, fig, historical_data, current_data, row, col):
        """Add heat wave events per year subplot."""
        # Calculate events per year
        historical_events = historical_data.groupby(
            historical_data['date'].dt.year)['is_heatwave'].sum()
        current_events = current_data.groupby(
            current_data['date'].dt.year)['is_heatwave'].sum()
        
        fig.add_trace(
            go.Scatter(
                x=['historical'] * len(historical_events),
                y=historical_events,
                mode='markers',
                name='1980-1989',
                marker=dict(color=self.colors['historical'], size=10)
            ),
            row=row, col=col
        )
        
        fig.add_trace(
            go.Scatter(
                x=['current'] * len(current_events),
                y=current_events,
                mode='markers',
                name='2015-2024',
                marker=dict(color=self.colors['current'], size=10)
            ),
            row=row, col=col
        )
        
        fig.update_xaxes(title_text='Period', row=row, col=col)
        fig.update_yaxes(title_text='Heat Wave Events per Year', row=row, col=col)

    def _add_seasonal_distribution(self, fig, historical_data, current_data, row, col):
        """Add seasonal heat wave distribution subplot."""
        # Calculate seasonal events
        historical_seasonal = historical_data.groupby(
            historical_data['date'].dt.month)['is_heatwave'].sum()
        current_seasonal = current_data.groupby(
            current_data['date'].dt.month)['is_heatwave'].sum()
        
        fig.add_trace(
            go.Bar(
                x=historical_seasonal.index,
                y=historical_seasonal,
                name='1980-1989',
                marker_color=self.colors['historical']
            ),
            row=row, col=col
        )
        
        fig.add_trace(
            go.Bar(
                x=current_seasonal.index,
                y=current_seasonal,
                name='2015-2024',
                marker_color=self.colors['current']
            ),
            row=row, col=col
        )
        
        fig.update_xaxes(title_text='Month', row=row, col=col)
        fig.update_yaxes(title_text='Heat Wave Events per Month', row=row, col=col)

def main():
    """Example usage of the visualizer."""
    visualizer = HeatWaveVisualizer()
    
    # Load your data here
    data = pd.read_csv('data/processed/heatwave_data.csv')
    data.index = pd.to_datetime(data['date'])
    
    # Create trend analysis
    trend_fig = visualizer.plot_trend_analysis(data)
    trend_fig.write_html('figures/heatwave_analysis/trend_analysis.html')

    # Create sample data
    historical_data = pd.DataFrame({
        'temperature': np.random.normal(298, 5, 1000),
        'is_heatwave': np.random.choice([0, 1], 1000),
        'date': pd.date_range('1981-01-01', '2010-12-31', periods=1000)
    })
    
    current_data = pd.DataFrame({
        'temperature': np.random.normal(299, 5, 500),
        'is_heatwave': np.random.choice([0, 1], 500),
        'date': pd.date_range('2011-01-01', '2019-12-31', periods=500)
    })
    
    # Create visualizer
    viz = HeatWaveVisualizer()
    
    # Generate plots
    viz.plot_heatwave_comparison(
        {'total_days': 45, 'num_events': 12},
        {'total_days': 78, 'num_events': 20},
        metric='days'
    )
    
    viz.plot_temperature_distribution(historical_data, current_data)

    # Create period comparison
    viz.create_period_comparison({
        '1980-1989': {
            'cash_transfer': {
                'mean_temperature': 25.0,
                'uncertainty': 1.0,
                'heat_wave_events': 10,
                'heat_wave_days': 20,
                'mean_duration': 3.0
            },
            'moderate': {
                'heat_wave_events': 5,
                'mean_duration': 2.0
            },
            'extreme': {
                'heat_wave_events': 2,
                'mean_duration': 1.5
            },
            'saws': {
                'heat_wave_events': 8,
                'mean_duration': 2.5
            }
        },
        '2015-2024': {
            'cash_transfer': {
                'mean_temperature': 26.0,
                'uncertainty': 1.2,
                'heat_wave_events': 15,
                'heat_wave_days': 30,
                'mean_duration': 3.5
            },
            'moderate': {
                'heat_wave_events': 7,
                'mean_duration': 2.2
            },
            'extreme': {
                'heat_wave_events': 3,
                'mean_duration': 1.8
            },
            'saws': {
                'heat_wave_events': 10,
                'mean_duration': 2.8
            }
        }
    })

if __name__ == "__main__":
    main()
