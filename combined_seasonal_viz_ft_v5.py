import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Set the style to match FT
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.labelcolor'] = '#333333'
plt.rcParams['text.color'] = '#333333'
plt.rcParams['xtick.color'] = '#666666'
plt.rcParams['ytick.color'] = '#666666'
plt.rcParams['grid.color'] = '#E6E6E6'
plt.rcParams['grid.linestyle'] = '-'
plt.rcParams['grid.alpha'] = 0.5
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.grid'] = True

# Create figure with three subplots
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 6))
fig.patch.set_facecolor('white')

# Colors in FT style
ft_coral = '#FF8E7F'
ft_blue = '#2E6E9E'

# Plot 1: Bara Mental Health Cases
bara_data = {'Season': ['Spring', 'Rest of Year'],
             'Cases': [4.5, 1.6]}
colors1 = [ft_coral, ft_blue]
bars1 = ax1.bar(bara_data['Season'], bara_data['Cases'], color=colors1)
ax1.set_title('Bara Mental Health Cases\nper Month', 
              fontsize=12, pad=15, color='#1A1A1A', fontweight='bold')
ax1.set_ylabel('Average Cases per Month', fontsize=10, color='#333333')
ax1.grid(axis='y', alpha=0.2)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.text(0.05, -0.25, 'Source: CHBAH Maternity 2023-2024\nSpring diff: 3.0',
         transform=ax1.transAxes, fontsize=8, color='#666666', ha='left', style='italic')

# Plot 2: Szabo Study Cases
szabo_data = {'Season': ['Spring', 'Rest of Year'],
              'Cases': [50.0, 40.67]}  # Corrected values
bars2 = ax2.bar(szabo_data['Season'], szabo_data['Cases'], color=colors1)
ax2.set_title('Szabo Study Cases\nper Month (1989)', 
              fontsize=12, pad=15, color='#1A1A1A', fontweight='bold')
ax2.set_ylabel('Average Cases per Month', fontsize=10, color='#333333')
ax2.grid(axis='y', alpha=0.2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.text(0.05, -0.25, 'Source: Szabo & Jones (1989)\nSpring diff: +9.3',
         transform=ax2.transAxes, fontsize=8, color='#666666', ha='left', style='italic')

# Plot 3: ERA5 Temperature Change
temp_data = {
    'Transition': ['Summer to\nAutumn', 'Autumn to\nWinter', 'Winter to\nSpring', 'Spring to\nSummer'],
    'Change': [-1.4, -2.8, 4.0, 0.8]
}

# Colors: blue for cooling transitions, coral for warming transitions
colors3 = [ft_blue, ft_blue, ft_coral, ft_blue]
bars3 = ax3.bar(range(len(temp_data['Transition'])), temp_data['Change'], color=colors3)

# Add value labels on top/bottom of bars
for bar in bars3:
    height = bar.get_height()
    va = 'bottom' if height >= 0 else 'top'
    y_offset = 0.1 if height >= 0 else -0.1
    ax3.text(bar.get_x() + bar.get_width()/2., height + y_offset,
             f'{height:.1f}°C',
             ha='center', va=va, color='#333333', fontsize=9)

# Customize the temperature plot
ax3.set_title('JHB Temperature Change\n(ERA5 2m Temperature)', 
              fontsize=12, pad=15, color='#1A1A1A', fontweight='bold')
ax3.set_ylabel('Temperature Change (°C)', fontsize=10, color='#333333')
ax3.set_xticks(range(len(temp_data['Transition'])))
ax3.set_xticklabels(temp_data['Transition'], color='#333333')
ax3.grid(axis='y', alpha=0.2)
ax3.set_ylim(-3.2, 4.5)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

# Add source and note information for temperature plot
ax3.text(0.05, -0.3, 
         'Source: ERA5 reanalysis (1989-2024)\nWinter-Spring rise: 4.0°C',
         transform=ax3.transAxes, fontsize=8, color='#666666', ha='left', style='italic')
ax3.text(0.95, -0.4,
         'Note: SON = September, October, November (Southern Hemisphere Spring)\nTemperature from ERA5 2m air temperature reanalysis',
         transform=ax3.transAxes, fontsize=8, color='#666666', ha='right', style='italic')

# Main title in FT style
plt.suptitle('Seasonal Comparison of Mental Health Cases in Johannesburg\nSpring (SON) vs Rest of Year',
             y=1.05, fontsize=14, color='#1A1A1A', weight='bold')

# Add value labels for first two plots
for ax, bars in [(ax1, bars1), (ax2, bars2)]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', color='#333333', fontsize=9)

# Adjust layout with more spacing
plt.tight_layout(w_pad=3)

# Save figure with high quality
plt.savefig('paper_figures_color/seasonal_comparison_ft.png',
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
