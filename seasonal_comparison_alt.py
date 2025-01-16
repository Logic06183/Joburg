import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from seasonal_comparison import calculate_seasonal_stats, bara_data, szabo_monthly

# Set style
plt.style.use('default')
colors = {'spring': '#FF6B35', 'other': '#4575B4'}

# ERA5 temperature data
era5_temps = {
    'Aug': 13.5,
    'Sep': 17.4,
    'Oct': 19.2,
    'Nov': 19.9,
    'Dec': 20.7
}

# 1. Line plot with monthly progression
plt.figure(figsize=(12, 6))
months = list(era5_temps.keys())
temps = list(era5_temps.values())

plt.plot(months, temps, marker='o', linewidth=2, color=colors['spring'])
plt.fill_between(months, temps, min(temps), alpha=0.2, color=colors['spring'])

plt.title('Temperature Progression: Winter to Summer\nJohannesburg ERA5 2m Temperature (1989-2024)', pad=20)
plt.ylabel('Temperature (°C)')
plt.grid(True, alpha=0.3)

# Add annotations for key transitions
plt.annotate(f'Winter-Spring\nChange: +{era5_temps["Nov"]-era5_temps["Aug"]:.1f}°C',
             xy=('Sep', 17), xytext=('Sep', 15),
             arrowprops=dict(facecolor='black', shrink=0.05),
             ha='center', va='top')

plt.annotate(f'Spring-Summer\nChange: +{era5_temps["Dec"]-era5_temps["Nov"]:.1f}°C',
             xy=('Dec', 20.7), xytext=('Dec', 22),
             arrowprops=dict(facecolor='black', shrink=0.05),
             ha='center', va='bottom')

plt.tight_layout()
plt.savefig('seasonal_temp_progression.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. Combined visualization with temperature curve and case counts
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[1, 1.5])

# Temperature curve on top
ax1.plot(months, temps, marker='o', linewidth=2, color=colors['spring'])
ax1.fill_between(months, temps, min(temps), alpha=0.2, color=colors['spring'])
ax1.set_title('Temperature and Mental Health Cases Progression', pad=20)
ax1.set_ylabel('Temperature (°C)')
ax1.grid(True, alpha=0.3)

# Bar plots below
spring_bara, rest_bara = calculate_seasonal_stats(bara_data, 'date')
spring_szabo, rest_szabo = calculate_seasonal_stats(szabo_monthly, 'month', 'admissions')

# Create grouped bar plot
datasets = ['Bara\n(2023-2024)', 'Szabo\n(1989)']
spring_vals = [spring_bara, spring_szabo]
rest_vals = [rest_bara, rest_szabo]

x = np.arange(len(datasets))
width = 0.35

ax2.bar(x - width/2, spring_vals, width, label='Spring', color=colors['spring'])
ax2.bar(x + width/2, rest_vals, width, label='Rest of Year', color=colors['other'])

ax2.set_ylabel('Average Cases per Month')
ax2.set_xticks(x)
ax2.set_xticklabels(datasets)
ax2.legend()
ax2.grid(True, alpha=0.3)

# Add percentage differences
for i, (spring, rest) in enumerate(zip(spring_vals, rest_vals)):
    pct_diff = ((spring - rest) / rest) * 100
    ax2.text(i, max(spring, rest) + 1, f'{pct_diff:+.1f}%',
             ha='center', va='bottom')

plt.tight_layout()
plt.savefig('seasonal_combined_view.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. Period comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Temperature changes by period
periods = {
    'Szabo (1989)': {'Winter-Spring': 3.7, 'Spring-Summer': 1.9},
    'UCT (2013-2019)': {'Winter-Spring': 6.2, 'Spring-Summer': 0.8},
    'All Years (1989-2024)': {'Winter-Spring': 6.4, 'Spring-Summer': 0.8}
}

# Create DataFrame for easier plotting
df_periods = pd.DataFrame(periods).T
df_periods.plot(kind='bar', ax=ax1, color=[colors['spring'], colors['other']])
ax1.set_title('Temperature Changes by Period')
ax1.set_ylabel('Temperature Change (°C)')
ax1.grid(True, alpha=0.3)
plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')

# Case counts by period
cases = {
    'Szabo (1989)': {'Spring': spring_szabo, 'Rest': rest_szabo},
    'Bara (2023-2024)': {'Spring': spring_bara, 'Rest': rest_bara}
}
df_cases = pd.DataFrame(cases).T
df_cases.plot(kind='bar', ax=ax2, color=[colors['spring'], colors['other']])
ax2.set_title('Mental Health Cases by Period')
ax2.set_ylabel('Average Cases per Month')
ax2.grid(True, alpha=0.3)
plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig('period_comparisons.png', dpi=300, bbox_inches='tight')
plt.close()
