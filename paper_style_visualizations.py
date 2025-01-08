import pandas as pd
import matplotlib.pyplot as plt
import calendar
import numpy as np

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
if not os.path.exists('paper_figures'):
    os.makedirs('paper_figures')

# Figure 1: Monthly Cases Bar Chart
plt.figure(figsize=(10, 6))
monthly_counts = df['month_name'].value_counts().reindex(
    [calendar.month_name[i] for i in range(1, 13)]
).fillna(0)

plt.bar(range(len(monthly_counts)), monthly_counts, color='gray', edgecolor='black')
plt.title('Figure 1: Monthly Distribution of Cases', pad=20)
plt.xlabel('Month')
plt.ylabel('Number of Cases')
plt.xticks(range(len(monthly_counts)), monthly_counts.index, rotation=45)
plt.ylim(0, max(monthly_counts) + 2)  # Add some padding to y-axis
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('paper_figures/figure1_monthly_cases.png')
plt.close()

# Figure 2: Cases by Season Bar Chart
plt.figure(figsize=(8, 6))
seasonal_counts = df['season'].value_counts().reindex(['Summer', 'Autumn', 'Winter', 'Spring'])
plt.bar(range(len(seasonal_counts)), seasonal_counts, color='gray', edgecolor='black')
plt.title('Figure 2: Seasonal Distribution of Cases', pad=20)
plt.xlabel('Season')
plt.ylabel('Number of Cases')
plt.xticks(range(len(seasonal_counts)), seasonal_counts.index)
plt.ylim(0, max(seasonal_counts) + 2)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('paper_figures/figure2_seasonal_cases.png')
plt.close()

# Figure 3: Expected vs Actual Cases Comparison
plt.figure(figsize=(10, 6))
expected_cases = len(df) / 4  # Equal distribution across seasons
seasons = ['Summer', 'Autumn', 'Winter', 'Spring']
actual_cases = seasonal_counts.reindex(seasons).values
expected_array = np.array([expected_cases] * 4)

x = np.arange(len(seasons))
width = 0.35

plt.bar(x - width/2, actual_cases, width, label='Actual Cases', color='gray', edgecolor='black')
plt.bar(x + width/2, expected_array, width, label='Expected Cases', color='lightgray', edgecolor='black')

plt.title('Figure 3: Expected vs Actual Cases by Season', pad=20)
plt.xlabel('Season')
plt.ylabel('Number of Cases')
plt.xticks(x, seasons)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add chi-square test results
from scipy import stats
chi2, p_value = stats.chisquare(actual_cases, expected_array)
plt.text(0.02, 0.98, f'χ² = {chi2:.3f}\np < {p_value:.3f}', 
         transform=plt.gca().transAxes, 
         verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig('paper_figures/figure3_expected_vs_actual.png')
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

print("\nAnalysis complete. Figures have been saved to the 'paper_figures' folder.")
