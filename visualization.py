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

class HeatWaveVisualizer:
    """
    Creates FT-styled visualizations for heat wave analysis.
    """
    
    def __init__(self, output_dir=None):
        """
        Initialize visualizer with output directory.
        
        Parameters:
        -----------
        output_dir : str or Path
            Directory to save generated figures
        """
        logger.debug("Initializing HeatWaveVisualizer")
        if output_dir is None:
            output_dir = Path.cwd() / 'figures' / 'heatwave_analysis'
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Output directory: {self.output_dir}")
        
    def _setup_style(self):
        """Configure matplotlib style for FT aesthetics."""
        plt.style.use('seaborn-v0_8')
        plt.rcParams.update({
            'font.family': FT_STYLE['font_family'],
            'figure.facecolor': FT_COLORS['background'],
            'axes.facecolor': FT_COLORS['background'],
            'axes.edgecolor': FT_COLORS['axis_grey'],
            'axes.labelcolor': FT_COLORS['dark_grey'],
            'xtick.color': FT_COLORS['mid_grey'],
            'ytick.color': FT_COLORS['mid_grey'],
            'grid.color': FT_STYLE['grid_color'],
            'grid.alpha': FT_STYLE['grid_alpha']
        })
    
    def _add_source_and_notes(self, fig, source_text, notes_text=None):
        """Add source attribution and notes to the figure."""
        fig.text(0.02, 0.02, f"Source: {source_text}", 
                fontsize=FT_STYLE['annotation_size'], 
                color=FT_COLORS['mid_grey'])
        
        if notes_text:
            fig.text(0.02, 0.04, f"Notes: {notes_text}", 
                    fontsize=FT_STYLE['annotation_size'], 
                    color=FT_COLORS['mid_grey'])
    
    def plot_heatwave_comparison(self, historical_data, current_data, 
                               metric='days', definition='SAWS'):
        """
        Create bar chart comparing heat wave metrics between periods.
        
        Parameters:
        -----------
        historical_data : dict
            Historical period heat wave metrics
        current_data : dict
            Current period heat wave metrics
        metric : str
            Type of metric to plot ('days' or 'events')
        definition : str
            Heat wave definition used ('SAWS' or '90th_percentile')
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Prepare data
        periods = ['Historical\n(1981-2010)', 'Current\n(2011-2019)']
        if metric == 'days':
            values = [historical_data['total_days'], current_data['total_days']]
            title = f'Heat Wave Days Comparison ({definition} Definition)'
            ylabel = 'Number of Heat Wave Days'
        else:
            values = [historical_data['num_events'], current_data['num_events']]
            title = f'Heat Wave Events Comparison ({definition} Definition)'
            ylabel = 'Number of Heat Wave Events'
            
        # Create bars
        bars = ax.bar(periods, values, color=FT_COLORS['main_red'])
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.0f}',
                   ha='center', va='bottom',
                   color=FT_COLORS['dark_grey'])
        
        # Styling
        ax.set_title(title, fontsize=FT_STYLE['title_size'], 
                    color=FT_COLORS['dark_grey'], pad=20)
        ax.set_ylabel(ylabel, fontsize=FT_STYLE['axis_title_size'])
        ax.grid(True, axis='y', alpha=FT_STYLE['grid_alpha'])
        
        # Add source and notes
        self._add_source_and_notes(
            fig,
            "ERA5 reanalysis data",
            f"Analysis using {definition} definition of heat waves at Rahima Moosa Hospital"
        )
        
        # Save figure
        plt.tight_layout()
        filename = f'heatwave_{metric}_{definition.lower()}.png'
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_temperature_distribution(self, historical_data, current_data):
        """Create temperature distribution comparison plot."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create density plots
        sns.kdeplot(data=historical_data['temperature'], 
                   label='Historical (1981-2010)',
                   color=FT_COLORS['main_red'],
                   ax=ax)
        sns.kdeplot(data=current_data['temperature'],
                   label='Current (2011-2019)',
                   color=FT_COLORS['light_red'],
                   ax=ax)
        
        # Styling
        ax.set_title('Temperature Distribution Comparison',
                    fontsize=FT_STYLE['title_size'],
                    color=FT_COLORS['dark_grey'])
        ax.set_xlabel('Temperature (°C)',
                     fontsize=FT_STYLE['axis_title_size'])
        ax.set_ylabel('Density',
                     fontsize=FT_STYLE['axis_title_size'])
        ax.legend(frameon=True, facecolor=FT_COLORS['background'])
        
        # Add source and notes
        self._add_source_and_notes(
            fig,
            "ERA5 reanalysis data",
            "Kernel density estimation of daily maximum temperatures"
        )
        
        # Save figure
        plt.tight_layout()
        plt.savefig(self.output_dir / 'temperature_distribution.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_interactive_dashboard(self, historical_data, current_data,
                                   saws_results, percentile_results):
        """Create interactive Plotly dashboard."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Heat Wave Days Comparison',
                'Temperature Distribution',
                'Heat Wave Events by Season',
                'Definition Comparison'
            )
        )
        
        # Heat Wave Days Comparison
        fig.add_trace(
            go.Bar(
                x=['Historical', 'Current'],
                y=[saws_results['historical']['total_days'],
                   saws_results['current']['total_days']],
                name='SAWS Definition',
                marker_color=FT_COLORS['main_red']
            ),
            row=1, col=1
        )
        
        # Temperature Distribution
        fig.add_trace(
            go.Histogram(
                x=historical_data['temperature'],
                name='Historical',
                opacity=0.75,
                marker_color=FT_COLORS['main_red']
            ),
            row=1, col=2
        )
        fig.add_trace(
            go.Histogram(
                x=current_data['temperature'],
                name='Current',
                opacity=0.75,
                marker_color=FT_COLORS['light_red']
            ),
            row=1, col=2
        )
        
        # Update layout
        fig.update_layout(
            template='none',
            plot_bgcolor=FT_COLORS['background'],
            paper_bgcolor=FT_COLORS['background'],
            font_family=FT_STYLE['font_family'],
            font_color=FT_COLORS['dark_grey'],
            showlegend=True
        )
        
        # Save dashboard
        fig.write_html(self.output_dir / 'interactive_dashboard.html')

    def plot_trend_analysis(self, data, title="Heat Wave Trend Analysis"):
        """
        Create a trend analysis plot showing the increasing frequency of heat waves.
        """
        # Create yearly aggregation
        yearly_data = data.resample('Y').sum()
        
        # Calculate trend line
        x = np.arange(len(yearly_data))
        z = np.polyfit(x, yearly_data['heat_wave_days'], 1)
        p = np.poly1d(z)
        
        fig = go.Figure()
        
        # Add bar chart for actual values
        fig.add_trace(go.Bar(
            x=yearly_data.index,
            y=yearly_data['heat_wave_days'],
            name='Heat Wave Days',
            marker_color=FT_COLORS['main_red']
        ))
        
        # Add trend line
        fig.add_trace(go.Scatter(
            x=yearly_data.index,
            y=p(x),
            name='Trend',
            line=dict(color=FT_COLORS['light_red'], dash='dash'),
            mode='lines'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Year",
            yaxis_title="Number of Heat Wave Days",
            template="plotly_white",
            showlegend=True,
            font=dict(family=FT_STYLE['font_family']),
            plot_bgcolor=FT_COLORS['background'],
            annotations=[
                dict(
                    x=0.02,
                    y=1.05,
                    xref="paper",
                    yref="paper",
                    text="Source: ERA5 Reanalysis Data",
                    showarrow=False,
                    font=dict(size=FT_STYLE['annotation_size'])
                )
            ]
        )
        
        return fig

    def _validate_input_data(self, df, period):
        """Validate input data for visualization."""
        logger.debug(f"Validating {period} data")
        
        # Check if DataFrame is empty
        if df.empty:
            raise ValueError(f"{period} data is empty")
        
        # Check required columns
        required_columns = ['temperature_celsius', 'date']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in {period} data: {missing_cols}")
        
        # Check data types
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            logger.warning(f"Converting date column to datetime in {period} data")
            df['date'] = pd.to_datetime(df['date'])
            
        if not pd.api.types.is_float_dtype(df['temperature_celsius']):
            logger.warning(f"Converting temperature to float in {period} data")
            df['temperature_celsius'] = df['temperature_celsius'].astype(float)
        
        # Check for missing values
        na_count = df['temperature_celsius'].isna().sum()
        if na_count > 0:
            logger.warning(f"Found {na_count} missing temperature values in {period} data")
        
        return df

    def create_period_comparison(self, historical_data, current_data):
        """Create period comparison visualization."""
        logger.debug("Creating period comparison visualization")
        try:
            # Validate input data
            historical_data = self._validate_input_data(historical_data, 'historical')
            current_data = self._validate_input_data(current_data, 'current')
            
            logger.debug(f"Historical data shape: {historical_data.shape}")
            logger.debug(f"Current data shape: {current_data.shape}")
            
            # Create the visualization
            logger.debug("Creating figure")
            fig = go.Figure()
            
            # Calculate summary statistics
            hist_mean = historical_data['temperature_celsius'].mean()
            curr_mean = current_data['temperature_celsius'].mean()
            temp_change = curr_mean - hist_mean
            
            # Add temperature distribution
            for data, period, color in [
                (historical_data, '1980-1989', '#990F3D'),
                (current_data, '2015-2024', '#FF8D8D')
            ]:
                logger.debug(f"Processing {period} data")
                temps = data['temperature_celsius'].dropna()
                mean_temp = temps.mean()
                std_temp = temps.std()
                
                logger.debug(f"Temperature range for {period}: {temps.min():.1f}°C to {temps.max():.1f}°C")
                logger.debug(f"Number of temperature readings for {period}: {len(temps)}")
                
                try:
                    fig.add_trace(
                        go.Histogram(
                            x=temps,
                            name=period,
                            nbinsx=30,
                            opacity=0.7,
                            marker_color=color,
                            histnorm='probability',
                            hovertemplate=(
                                f"Period: {period}<br>" +
                                "Temperature: %{x:.1f}°C<br>" +
                                "Proportion: %{y:.1%}<br>" +
                                f"Mean: {mean_temp:.1f}°C<br>" +
                                f"Std Dev: {std_temp:.1f}°C<br>" +
                                "<extra></extra>"
                            )
                        )
                    )
                    logger.debug(f"Successfully added trace for {period}")
                except Exception as trace_error:
                    logger.error(f"Error adding trace for {period}: {str(trace_error)}")
                    raise

            # Create title with key findings
            title_text = (
                "Temperature Distribution at Rahima Moosa Hospital<br>" +
                "<span style='font-size: 14px;'>" +
                "Comparison of Historical (1980-1989) vs Recent (2015-2024) Daily Maximum Temperatures<br>" +
                f"<span style='color: {FT_COLORS['main_red']};'>" +
                f"Mean temperature increase: {temp_change:+.1f}°C" +
                "</span></span>"
            )

            # Update layout
            logger.debug("Updating figure layout")
            try:
                fig.update_layout(
                    title={
                        'text': title_text,
                        'y': 0.95,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    },
                    xaxis_title={
                        'text': 'Maximum Daily Temperature (°C)',
                        'font': {'size': 12}
                    },
                    yaxis_title={
                        'text': 'Proportion of Days',
                        'font': {'size': 12}
                    },
                    template='plotly_white',
                    height=800,
                    width=1200,
                    paper_bgcolor='#FFF1E5',
                    plot_bgcolor='#FFF1E5',
                    showlegend=True,
                    legend={
                        'orientation': 'h',
                        'yanchor': 'bottom',
                        'y': 1.02,
                        'xanchor': 'right',
                        'x': 1,
                        'bgcolor': 'rgba(255, 255, 255, 0.8)',
                        'bordercolor': FT_COLORS['axis_grey'],
                        'borderwidth': 1
                    },
                    annotations=[
                        # Source attribution
                        {
                            'text': (
                                'Source: ERA5 reanalysis data (maximum daily temperature)<br>' +
                                'Analysis shows changes in temperature distribution over 35-year period during summer and spring'
                            ),
                            'x': 0,
                            'y': -0.15,
                            'xref': 'paper',
                            'yref': 'paper',
                            'showarrow': False,
                            'font': {'size': 10, 'color': FT_COLORS['mid_grey']},
                            'align': 'left'
                        }
                    ],
                    margin={'t': 100, 'b': 100}
                )
                
                # Update axes for better readability
                fig.update_xaxes(
                    gridcolor='rgba(128,128,128,0.1)',
                    tickfont={'size': 10},
                    tickformat='.0f'
                )
                fig.update_yaxes(
                    gridcolor='rgba(128,128,128,0.1)',
                    tickfont={'size': 10},
                    tickformat='.1%'
                )
                
                logger.debug("Successfully updated figure layout")
            except Exception as layout_error:
                logger.error(f"Error updating layout: {str(layout_error)}")
                raise

            # Save with proper HTML structure
            logger.debug("Saving visualization")
            try:
                timestamp = int(time.time())
                output_path = self.save_visualization(fig, f'period_comparison_{timestamp}.html')
                logger.debug(f"Successfully saved visualization to {output_path}")
            except Exception as save_error:
                logger.error(f"Error saving visualization: {str(save_error)}")
                raise
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating visualization: {str(e)}")
            raise

    def generate_html_wrapper(self, plotly_html):
        """Wrap plotly HTML with proper metadata and viewport settings"""
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Heat Wave Analysis - Rahima Moosa Hospital</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background-color: #FFF1E5;
            font-family: Arial, sans-serif;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        {plotly_html}
    </div>
</body>
</html>"""
        return html_template

    def save_visualization(self, fig, filename):
        """Save visualization with proper HTML wrapper"""
        # Generate the plotly HTML
        plotly_html = fig.to_html(include_plotlyjs=True, full_html=False)
        
        # Wrap it with proper HTML
        full_html = self.generate_html_wrapper(plotly_html)
        
        # Save to file
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        return output_path

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
    viz.create_period_comparison(historical_data, current_data)

if __name__ == "__main__":
    main()
