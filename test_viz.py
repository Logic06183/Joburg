import plotly.graph_objects as go
from pathlib import Path
import pandas as pd
import numpy as np

# Create sample data
np.random.seed(42)
historical = np.random.normal(25, 5, 1000)
current = np.random.normal(27, 5, 1000)

# Create figure
fig = go.Figure()

# Add traces
fig.add_trace(go.Histogram(
    x=historical,
    name='1980-1989',
    nbinsx=30,
    opacity=0.7,
    marker_color='#990F3D',
    histnorm='probability'
))

fig.add_trace(go.Histogram(
    x=current,
    name='2015-2024',
    nbinsx=30,
    opacity=0.7,
    marker_color='#FF8D8D',
    histnorm='probability'
))

# Update layout
fig.update_layout(
    title='Heat Wave Analysis - Test',
    xaxis_title='Temperature (°C)',
    yaxis_title='Proportion of Days',
    template='plotly_white',
    height=800,
    width=1200
)

# Create output directory if it doesn't exist
output_dir = Path('figures/test')
output_dir.mkdir(parents=True, exist_ok=True)

# Save figure
fig.write_html(output_dir / 'test_viz.html')
