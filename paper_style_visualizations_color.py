import pandas as pd
import matplotlib.pyplot as plt
import calendar
import numpy as np

# Set style for better-looking plots
plt.style.use('default')
color_palette = ['#2ecc71', '#3498db', '#9b59b6', '#f1c40f', '#e74c3c']

# Create the data
data = {
    'date': ['30-Jan-24', '09-Feb-24', '14-Feb-24', '22-Apr-24', '13-May-24', '14-May-24', 
             '17-May-24', '06-Jun-24', '26-Jun-24', '27-Jun-24', '04-Jul-24', '11-Jul-24',
             '15-Jul-24', '24-Aug-24', '25-Aug-24', '24-Sep-24', '24-Oct-24', '26-Oct-24',
             '27-Oct-24', '28-Oct-24', '01-Nov-24', '10-Nov-24', '10-Nov-24', '11-Nov-24',
             '11-Nov-24', '21-Nov-24', '24-Nov-24', '24-Nov-24', '25-Nov-24']
}

# Create DataFrame
df = pd.DataFrame(data)

# Convert date to datetime
df['date'] = pd.to_datetime(df['date'], format='%d-%b-%y')

# Add month and season columns
df['month'] = df['date'].dt.month
df['month_name'] = df['date'].dt.strftime('%B')

# Define seasons (Southern Hemisphere)
def get_season(month):
    if month in [9, 10, 11]:
        return 'Spring'
    elif month in [12, 1, 2]:
        return 'Summer'
    elif month in [3, 4, 5]:
        return 'Autumn'
    else:
        return 'Winter'

df['season'] = df['month'].apply(get_season)

# Create visualizations directory if it doesn't exist
import os
if not os.path.exists('paper_figures_color'):
    os.makedirs('paper_figures_color')

# Figure 1: Monthly Cases Bar Chart
plt.figure(figsize=(12, 7))
monthly_counts = df['month_name'].value_counts().reindex(
    [calendar.month_name[i] for i in range(1, 13)]
).fillna(0)

bars = plt.bar(range(len(monthly_counts)), monthly_counts, 
               color='#3498db', alpha=0.7, 
               edgecolor='#2980b9', linewidth=1.5)

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height)}',
             ha='center', va='bottom')

plt.title('Monthly Distribution of Cases (2024)', 
          fontsize=14, pad=20, fontweight='bold')
plt.xlabel('Month', fontsize=12)
plt.ylabel('Number of Cases', fontsize=12)
plt.xticks(range(len(monthly_counts)), monthly_counts.index, 
           rotation=45, ha='right')
plt.ylim(0, max(monthly_counts) + 2)
plt.grid(axis='y', linestyle='--', alpha=0.3)
plt.tight_layout()
plt.savefig('paper_figures_color/figure1_monthly_cases.png', dpi=300, bbox_inches='tight')
plt.close()

# Figure 2: Cases by Season Bar Chart
plt.figure(figsize=(10, 7))
seasonal_counts = df['season'].value_counts().reindex(['Summer', 'Autumn', 'Winter', 'Spring'])

bars = plt.bar(range(len(seasonal_counts)), seasonal_counts,
               color=['#f1c40f', '#e67e22', '#3498db', '#2ecc71'],
               alpha=0.7, edgecolor='#34495e', linewidth=1.5)

# Add value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height)}',
             ha='center', va='bottom')

plt.title('Seasonal Distribution of Cases', 
          fontsize=14, pad=20, fontweight='bold')
plt.xlabel('Season', fontsize=12)
plt.ylabel('Number of Cases', fontsize=12)
plt.xticks(range(len(seasonal_counts)), seasonal_counts.index, fontsize=10)
plt.ylim(0, max(seasonal_counts) + 2)
plt.grid(axis='y', linestyle='--', alpha=0.3)
plt.tight_layout()
plt.savefig('paper_figures_color/figure2_seasonal_cases.png', dpi=300, bbox_inches='tight')
plt.close()

# Figure 3: Expected vs Actual Cases Comparison
plt.figure(figsize=(12, 7))
expected_cases = len(df) / 4
seasons = ['Summer', 'Autumn', 'Winter', 'Spring']
actual_cases = seasonal_counts.reindex(seasons).values
expected_array = np.array([expected_cases] * 4)

x = np.arange(len(seasons))
width = 0.35

bars1 = plt.bar(x - width/2, actual_cases, width, 
                label='Actual Cases', 
                color=['#f1c40f', '#e67e22', '#3498db', '#2ecc71'],
                alpha=0.7, edgecolor='#34495e', linewidth=1.5)
bars2 = plt.bar(x + width/2, expected_array, width, 
                label='Expected Cases',
                color='#95a5a6', alpha=0.4, 
                edgecolor='#34495e', linewidth=1.5)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom')

plt.title('Expected vs Actual Cases by Season', 
          fontsize=14, pad=20, fontweight='bold')
plt.xlabel('Season', fontsize=12)
plt.ylabel('Number of Cases', fontsize=12)
plt.xticks(x, seasons, fontsize=10)
plt.legend(fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.3)

# Add chi-square test results with improved styling
from scipy import stats
chi2, p_value = stats.chisquare(actual_cases, expected_array)
plt.text(0.02, 0.95, 
         f'Statistical Analysis:\nχ² = {chi2:.3f}\np < {p_value:.3f}', 
         transform=plt.gca().transAxes,
         fontsize=10,
         verticalalignment='top',
         bbox=dict(boxstyle='round,pad=0.5',
                  facecolor='white',
                  alpha=0.8,
                  edgecolor='#34495e'))

plt.tight_layout()
plt.savefig('paper_figures_color/figure3_expected_vs_actual.png', dpi=300, bbox_inches='tight')
plt.close()

print("\nVisualization Results:")
print("=====================")
print("\nFigure 1 - Monthly Distribution:")
for month, count in monthly_counts.items():
    print(f"{month}: {count:.0f} cases")

print("\nFigure 2 - Seasonal Distribution:")
for season, count in seasonal_counts.items():
    print(f"{season}: {count:.0f} cases")

print("\nFigure 3 - Statistical Comparison:")
print(f"Chi-square statistic: {chi2:.3f}")
print(f"p-value: {p_value:.3f}")
print("\nExpected vs Actual Cases:")
for season, actual, expected in zip(seasons, actual_cases, expected_array):
    print(f"{season}:")
    print(f"  Actual: {actual:.0f}")
    print(f"  Expected: {expected:.1f}")
    print(f"  Difference: {actual - expected:.1f}")

print("\nAnalysis complete. Figures have been saved to the 'paper_figures_color' folder.")
