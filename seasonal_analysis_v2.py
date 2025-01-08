import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from datetime import datetime
import calendar

# Create the data
data = {
    'date': ['30-Jan-24', '09-Feb-24', '14-Feb-24', '22-Apr-24', '13-May-24', '14-May-24', 
             '17-May-24', '06-Jun-24', '26-Jun-24', '27-Jun-24', '04-Jul-24', '11-Jul-24',
             '15-Jul-24', '24-Aug-24', '25-Aug-24', '24-Sep-24', '24-Oct-24', '26-Oct-24',
             '27-Oct-24', '28-Oct-24', '01-Nov-24', '10-Nov-24', '10-Nov-24', '11-Nov-24',
             '11-Nov-24', '21-Nov-24', '24-Nov-24', '24-Nov-24', '25-Nov-24'],
    'diagnosis': ['schizophrenia', 'syncope spells', 'post partum pyschosis', 'seizure',
                 'seizure', 'anxiety', 'substance use', 'syncope', 'depression', 'low mood',
                 'depression', 'low mood', 'anxiety', 'seizure', 'seizure', 'parasuicide',
                 'seizure', 'seizure', 'parasuicide', 'parasuicide', 'parasuicide', 'syncope',
                 'syncope', 'anxiety', 'pyschogenic seizures', 'psychotic episode',
                 'parasuicide', 'anxiety', 'depression']
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
if not os.path.exists('visualizations'):
    os.makedirs('visualizations')

# 1. Seasonal Distribution Analysis
seasonal_counts = df['season'].value_counts()
expected_counts = pd.Series([len(df)/4] * 4, index=seasonal_counts.index)

# Chi-square test for seasonal distribution
chi2, p_value = stats.chisquare(seasonal_counts, expected_counts)

# Visualize seasonal distribution
plt.figure(figsize=(10, 6))
seasonal_counts.plot(kind='bar')
plt.title('Seasonal Distribution of Admissions')
plt.xlabel('Season')
plt.ylabel('Number of Admissions')
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('visualizations/seasonal_distribution.png')
plt.close()

# 2. Monthly Distribution
plt.figure(figsize=(12, 6))
monthly_counts = df['month_name'].value_counts().reindex(
    [calendar.month_name[i] for i in range(1, 13)]
)
monthly_counts.plot(kind='bar')
plt.title('Monthly Distribution of Admissions')
plt.xlabel('Month')
plt.ylabel('Number of Admissions')
plt.xticks(rotation=45)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('visualizations/monthly_distribution.png')
plt.close()

# 3. Diagnosis by Season
diagnosis_season = pd.crosstab(df['diagnosis'], df['season'])
chi2_diag_season, p_value_diag_season, dof, expected = stats.chi2_contingency(diagnosis_season)

# Visualize diagnosis distribution by season
plt.figure(figsize=(12, 6))
diagnosis_season.plot(kind='bar', stacked=True)
plt.title('Diagnosis Distribution by Season')
plt.xlabel('Diagnosis')
plt.ylabel('Number of Cases')
plt.legend(title='Season', bbox_to_anchor=(1.05, 1))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('visualizations/diagnosis_by_season.png')
plt.close()

# Print Statistical Analysis Results
print("\nStatistical Analysis Results:")
print("============================")

print("\n1. Seasonal Distribution Analysis:")
print(f"Chi-square statistic: {chi2:.2f}")
print(f"p-value: {p_value:.4f}")
print("\nSeasonal Counts:")
for season, count in seasonal_counts.items():
    expected = len(df)/4
    print(f"{season}:")
    print(f"  Observed: {count}")
    print(f"  Expected: {expected:.1f}")
    print(f"  Difference: {count - expected:.1f}")

print("\n2. Monthly Distribution:")
print("\nMonthly Counts:")
for month, count in monthly_counts.items():
    if pd.notna(count):
        print(f"{month}: {count:.0f} admissions")

print("\n3. Diagnosis by Season Analysis:")
print(f"Chi-square statistic: {chi2_diag_season:.2f}")
print(f"p-value: {p_value_diag_season:.4f}")
print(f"Degrees of freedom: {dof}")

print("\nDiagnosis Distribution by Season:")
print(diagnosis_season)

# Calculate percentages for each season
season_percentages = diagnosis_season.div(diagnosis_season.sum(axis=0), axis=1) * 100
print("\nPercentage Distribution by Season:")
print(season_percentages.round(1))

print("\nAnalysis complete. Visualizations have been saved to the 'visualizations' folder.")
