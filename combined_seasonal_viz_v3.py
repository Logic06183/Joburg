import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Create figure with three subplots, making it wider to avoid overlap
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 6))

# Plot 1: Bara Mental Health Cases
bara_data = {'Season': ['Spring', 'Rest of Year'],
             'Cases': [4.5, 1.6]}
colors1 = ['#FF7F50', '#4169E1']
ax1.bar(bara_data['Season'], bara_data['Cases'], color=colors1)
ax1.set_title('Bara Mental Health Cases\nper Month')
ax1.set_ylabel('Average Cases per Month')
ax1.grid(axis='y', alpha=0.2)
ax1.text(0.05, -0.15, 'Source: CHBAH Maternity 2023-2024\nSpring diff: 3.0',
         transform=ax1.transAxes, fontsize=8, ha='left')

# Plot 2: Szabo Study Cases
szabo_data = {'Season': ['Spring', 'Rest of Year'],
              'Cases': [40, 36]}  # From Szabo & Jones 1989 data
ax2.bar(szabo_data['Season'], szabo_data['Cases'], color=colors1)
ax2.set_title('Szabo Study Cases\nper Month (1989)')
ax2.set_ylabel('Average Cases per Month')
ax2.grid(axis='y', alpha=0.2)
ax2.text(0.05, -0.15, 'Source: Szabo & Jones (1989)\nSpring diff: +4.7',
         transform=ax2.transAxes, fontsize=8, ha='left')

# Plot 3: ERA5 Temperature Change
temp_data = {
    'Transition': ['Summer to\nAutumn', 'Autumn to\nWinter', 'Winter to\nSpring', 'Spring to\nSummer'],
    'Change': [-1.4, -2.8, 4.0, 0.8]
}

# Colors: blue for cooling transitions, coral for warming transitions
colors3 = ['#4169E1', '#4169E1', '#FF7F50', '#4169E1']
bars = ax3.bar(range(len(temp_data['Transition'])), temp_data['Change'], color=colors3)

# Add value labels on top/bottom of bars with increased spacing
for bar in bars:
    height = bar.get_height()
    va = 'bottom' if height >= 0 else 'top'
    y_offset = 0.1 if height >= 0 else -0.1
    ax3.text(bar.get_x() + bar.get_width()/2., height + y_offset,
             f'{height:.1f}°C',
             ha='center', va=va)

# Customize the temperature plot
ax3.set_title('JHB Temperature Change\n(ERA5 2m Temperature)')
ax3.set_ylabel('Temperature Change (°C)')
ax3.set_xticks(range(len(temp_data['Transition'])))
ax3.set_xticklabels(temp_data['Transition'])
ax3.grid(axis='y', alpha=0.2)
ax3.set_ylim(-3.2, 4.5)  # Adjusted to avoid text overlap

# Add source and note information for temperature plot with adjusted spacing
ax3.text(0.05, -0.15, 
         'Source: ERA5 reanalysis (1989-2024)\nWinter-Spring rise: 4.0°C',
         transform=ax3.transAxes, fontsize=8, ha='left')
ax3.text(0.95, -0.25,
         'Note: SON = September, October, November (Southern Hemisphere Spring)\nTemperature from ERA5 2m air temperature reanalysis',
         transform=ax3.transAxes, fontsize=8, ha='right')

# Main title
plt.suptitle('Seasonal Comparison of Mental Health Cases in Johannesburg\nSpring (SON) vs Rest of Year',
             y=1.05, fontsize=14)

# Adjust layout with more spacing
plt.tight_layout(w_pad=3)  # Increased spacing between subplots

# Save figure
plt.savefig('paper_figures_color/seasonal_comparison_combined_v3.png',
            dpi=300, bbox_inches='tight')
plt.close()
