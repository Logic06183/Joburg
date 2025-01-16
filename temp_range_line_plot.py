import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# Set up FT style
mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['axes.grid'] = True
mpl.rcParams['grid.alpha'] = 0.3
mpl.rcParams['grid.color'] = '#666666'
mpl.rcParams['axes.labelcolor'] = '#666666'
mpl.rcParams['xtick.color'] = '#666666'
mpl.rcParams['ytick.color'] = '#666666'

# Data from the temperature range analysis
data = {
    'temp_range': ['12-16°C', '16-20°C', '20-24°C', '24-28°C', '28-32°C'],
    'cases_per_day': [0.08, 0.06, 0.08, 0.10, 0.15]
}

df = pd.DataFrame(data)

# Create the figure and axis
fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
ax.set_facecolor('white')

# Create line plot with FT blue color
ft_blue = '#0F5499'
ax.plot(df['temp_range'], df['cases_per_day'], marker='o', linewidth=2.5, 
       markersize=8, color=ft_blue)

# Customize the plot
ax.set_title('Temperature Range vs Mental Health Cases per Day\nat a Tertiary Level Hospital in Johannesburg', 
           pad=20, fontsize=14, fontweight='bold', color='#1A1A1A')
ax.set_xlabel('Temperature Range (°C)', fontsize=12)
ax.set_ylabel('Cases per Day', fontsize=12)

# Rotate x-axis labels
ax.tick_params(axis='x', rotation=0)

# Add small date note at bottom
plt.figtext(0.02, 0.02, 'Data period: 2023 to 2024', 
            fontsize=8, color='#666666')

# Adjust layout
plt.tight_layout()

# Save the plot with high DPI
plt.savefig('temperature_range_line_plot.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.close()
