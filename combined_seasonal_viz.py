import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Create figure with three subplots
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

# Plot 1: Bara Mental Health Cases
bara_data = {'Season': ['Spring', 'Rest of Year'],
             'Cases': [4.5, 1.6]}
colors1 = ['#FF7F50', '#4169E1']
ax1.bar(bara_data['Season'], bara_data['Cases'], color=colors1)
ax1.set_title('Bara Mental Health Cases\nper Month')
ax1.set_ylabel('Average Cases per Month')
ax1.grid(axis='y', alpha=0.2)
ax1.text(0.05, -0.2, 'Source: CHBAH Maternity 2023-2024\nSpring diff: 3.0',
         transform=ax1.transAxes, fontsize=8, ha='left')

# Plot 2: Szabo Study Cases
szabo_data = {'Season': ['Spring', 'Rest of Year'],
              'Cases': [40, 36]}
ax2.bar(szabo_data['Season'], szabo_data['Cases'], color=colors1)
ax2.set_title('Szabo Study Cases\nper Month (1989)')
ax2.set_ylabel('Average Cases per Month')
ax2.grid(axis='y', alpha=0.2)
ax2.text(0.05, -0.2, 'Source: Szabo & Jones (1989)\nSpring diff: +4.7',
         transform=ax2.transAxes, fontsize=8, ha='left')

# Plot 3: ERA5 Temperature Change
temp_data = {'Transition': ['Winter to\nSpring', 'Spring to\nSummer'],
             'Change': [4.0, 0.8]}
ax3.bar(temp_data['Transition'], temp_data['Change'], color=colors1)
ax3.set_title('JHB Temperature Change\n(ERA5 2m Temperature)')
ax3.set_ylabel('Temperature Change (°C)')
ax3.grid(axis='y', alpha=0.2)
ax3.text(0.05, -0.2, 'Source: ERA5 reanalysis (1989-2024)\nWinter-Spring rise: 6.4°C',
         transform=ax3.transAxes, fontsize=8, ha='left')
ax3.text(0.95, -0.25, 'Note: SON = September, October, November (Southern Hemisphere Spring)\nTemperature from ERA5 2m air temperature reanalysis',
         transform=ax3.transAxes, fontsize=8, ha='right')

# Main title
plt.suptitle('Seasonal Comparison of Mental Health Cases in Johannesburg\nSpring (SON) vs Rest of Year',
             y=1.05, fontsize=14)

# Adjust layout
plt.tight_layout()

# Save figure
plt.savefig('paper_figures_color/seasonal_comparison_combined.png',
            dpi=300, bbox_inches='tight')
plt.close()
