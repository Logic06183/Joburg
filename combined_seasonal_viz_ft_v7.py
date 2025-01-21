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
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 15))
fig.patch.set_facecolor('white')

# Colors in FT style
ft_coral = '#FF8E7F'
ft_blue = '#2E6E9E'

# Plot 1: Current Cases
bara_data = {'Season': ['Spring', 'Rest of Year'],
             'Cases': [4.5, 1.6]}
colors1 = [ft_coral, ft_blue]
x1 = np.array([0, 0.6])  # Reduced spacing between bars
bars1 = ax1.bar(x1, bara_data['Cases'], color=colors1, width=0.25)  # Reduced width
ax1.set_xticks(x1)
ax1.set_xticklabels(bara_data['Season'])
ax1.set_title('Cases in Tertiary Facility\n(2023-2024)', 
              fontsize=12, pad=15, color='#1A1A1A', fontweight='bold')
ax1.set_ylabel('Average Cases per Month', fontsize=10, color='#333333')
ax1.grid(axis='y', alpha=0.2)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.text(0.05, -0.25, 'Source: Maternity Ward in Tertiary Hospital, Johannesburg (2023-2024)\nSpring diff: 3.0',
         transform=ax1.transAxes, fontsize=8, color='#666666', ha='left', style='italic')

# Plot 2: Historical Cases
szabo_data = {'Season': ['Spring', 'Rest of Year'],
              'Cases': [50.0, 40.67]}
x2 = np.array([0, 0.6])  # Reduced spacing between bars
bars2 = ax2.bar(x2, szabo_data['Cases'], color=colors1, width=0.25)  # Reduced width
ax2.set_xticks(x2)
ax2.set_xticklabels(szabo_data['Season'])
ax2.set_title('Cases in Tertiary Facility\n(1989)', 
              fontsize=12, pad=15, color='#1A1A1A', fontweight='bold')
ax2.set_ylabel('Average Cases per Month', fontsize=10, color='#333333')
ax2.grid(axis='y', alpha=0.2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.text(0.05, -0.25, 'Source: Maternity Ward in Tertiary Hospital, Johannesburg (1989)\nSpring diff: +9.3',
         transform=ax2.transAxes, fontsize=8, color='#666666', ha='left', style='italic')

# Plot 3: ERA5 Temperature Change
temp_data = {
    'Transition': ['Winter to\nSpring', 'Spring to\nSummer', 'Summer to\nAutumn', 'Autumn to\nWinter'],
    'Change': [4.0, 2.8, -0.8, -1.4]  # Making cooling transitions negative
}

# Colors: coral for Winter-Spring, blue for others
colors3 = [ft_coral] + [ft_blue] * 3
x3 = np.array([0, 0.6, 1.2, 1.8])  # Positions for all four bars
bars3 = ax3.bar(x3, temp_data['Change'], color=colors3, width=0.25)  # Reduced width

# Add value labels on top or bottom of bars depending on value
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
ax3.set_xticks(x3)
ax3.set_xticklabels(temp_data['Transition'], color='#333333')
ax3.grid(axis='y', alpha=0.2)
ax3.set_ylim(-2, 4.5)  # Updated y-axis range to show negative values
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

# Add source and note information for temperature plot
ax3.text(0.05, -0.3, 
         'Source: ERA5 reanalysis (1989-2024)\nWinter-Spring rise: 4.0°C vs. other transitions: 2.8°C, -0.8°C, -1.4°C',
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
plt.tight_layout(h_pad=1)

# Save figure with high quality
plt.savefig('paper_figures_color/seasonal_comparison_ft.png',
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
