import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import calendar
import numpy as np
from scipy.stats import chi2_contingency, fisher_exact

# Set publication-ready style
plt.style.use('seaborn-v0_8-paper')
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 300,
    'figure.figsize': [8.5, 6],  # Standard publication figure size
    'axes.linewidth': 1,
    'lines.linewidth': 1.5
})

# Define diagnosis groupings
diagnosis_groups = {
    'Depression': ['depression', 'depression ', 'low mood'],
    'Psychogenic Non-Epileptic Seizures': ['seizure', 'seizure ', 'syncope', 'syncope spells', 'pyschogenic seizures'],
    'Anxiety': ['anxiety', 'panic attack'],
    'Parasuicide': ['parasuicide'],
    'Psychosis': ['psychotic episode', 'schizophrenia', 'post partum pyschosis', 'substance use']
}

# Read the Excel file
df = pd.read_excel('10122024 mental health issues in obstetrics final final.xlsx')

# Convert date to datetime
df['date'] = pd.to_datetime(df['date'])

# Function to determine season in Southern Hemisphere
def get_season(month):
    if month in [12, 1, 2]:
        return 'Summer'
    elif month in [3, 4, 5]:
        return 'Autumn'
    elif month in [6, 7, 8]:
        return 'Winter'
    else:
        return 'Spring'

# Function to map diagnosis to group
def map_diagnosis_to_group(diagnosis):
    for group, diagnoses in diagnosis_groups.items():
        if diagnosis in diagnoses:
            return group
    return 'Other'

# Add month and season columns
df['Month'] = df['date'].dt.month
df['Month_Name'] = df['Month'].apply(lambda x: calendar.month_name[x])
df['Season'] = df['Month'].apply(get_season)

# Add diagnosis group column
df['diagnosis_group'] = df['diagnosis'].apply(map_diagnosis_to_group)

# Create contingency table with grouped diagnoses
seasonal_diagnosis = pd.crosstab(df['Season'], df['diagnosis_group'])
seasonal_diagnosis = seasonal_diagnosis.reindex(['Summer', 'Autumn', 'Winter', 'Spring'])

# Perform chi-square test
chi2, p_value, dof, expected = chi2_contingency(seasonal_diagnosis)

# Create 2x2 contingency table for Fisher's exact test (Spring vs Other Seasons)
spring_cases = len(df[df['Season'] == 'Spring'])
other_cases = len(df[df['Season'] != 'Spring'])
total_cases = len(df)
expected_per_group = total_cases / 4

fisher_table = np.array([[spring_cases, other_cases],
                        [expected_per_group, expected_per_group * 3]])
fisher_stat, fisher_p = fisher_exact(fisher_table)

# Create the visualization
fig = plt.figure(figsize=(8.5, 6.5))  # Slightly taller to accommodate source text
gs = fig.add_gridspec(1, 2, width_ratios=[1.5, 1], wspace=0.3)

# Plot the stacked bar chart
ax1 = fig.add_subplot(gs[0])

# Use colorblind-friendly palette
colors = sns.color_palette("colorblind", n_colors=len(diagnosis_groups))
seasonal_diagnosis.plot(kind='bar', stacked=True, ax=ax1, color=colors)

# Customize the plot
ax1.set_title('Seasonal Distribution of Mental Health Diagnoses', pad=20)
ax1.set_xlabel('Season')
ax1.set_ylabel('Number of Cases')
ax1.tick_params(axis='x', rotation=45)

# Add value labels on the bars
for c in ax1.containers:
    labels = [int(v.get_height()) if v.get_height() > 0 else '' for v in c]
    ax1.bar_label(c, labels=labels, label_type='center', fontsize=9)

# Remove top and right spines
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# Add gridlines
ax1.yaxis.grid(True, linestyle='--', alpha=0.7)

# Create a separate axes for the legend and statistical information
ax2 = fig.add_subplot(gs[1])
ax2.axis('off')

# Format statistical information
n = seasonal_diagnosis.sum().sum()
min_dim = min(seasonal_diagnosis.shape) - 1
stat_text = 'Statistical Analysis:\n\n'
stat_text += f'χ² test: {chi2:.1f}, p = {p_value:.3f}\n'
stat_text += f'Fisher\'s exact test: p = {fisher_p:.3f}\n\n'
stat_text += f'Distribution:\n'
stat_text += f'Spring: {spring_cases} ({(spring_cases/total_cases*100):.1f}%)\n'
stat_text += f'Other: {other_cases} ({(other_cases/total_cases*100):.1f}%)\n'
stat_text += f'Effect size (Cramer\'s V): {np.sqrt(chi2 / (n * min_dim)):.3f}'

# Add statistical text box
ax2.text(0, 0.7, stat_text,
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', pad=10),
         ha='left', va='center', fontsize=10)

# Add legend with improved formatting
handles, labels = ax1.get_legend_handles_labels()
ax2.legend(handles, labels, 
          title='Diagnosis Groups',
          loc='center',
          bbox_to_anchor=(0.5, 0.3),
          frameon=False,
          title_fontsize=11)

# Add source information with better positioning
plt.figtext(0.02, -0.05, 
           'Data source: Charlotte Maxeke Johannesburg Academic Hospital Mental Health Records (2024)',
           fontsize=8, style='italic')

# Adjust layout and save with extra bottom margin
plt.savefig('diagnosis_distribution_grouped.png', 
            dpi=300, 
            bbox_inches='tight',
            facecolor='white',
            edgecolor='none',
            pad_inches=0.2)  # Add padding to prevent text cutoff

# Print detailed statistical analysis
print("\nDetailed Statistical Analysis (Grouped Diagnoses):")
print("-" * 60)

print("\nDiagnosis Group Distribution:")
grouped_counts = df['diagnosis_group'].value_counts()
for group, count in grouped_counts.items():
    percentage = round((count / len(df) * 100), 1)
    print(f"{group}: {count} cases ({percentage}%)")

print("\nSeasonal Distribution by Diagnosis Group:")
print(seasonal_diagnosis)

print("\nPeak Seasons by Diagnosis Group:")
for group in diagnosis_groups.keys():
    group_data = df[df['diagnosis_group'] == group]
    if len(group_data) > 0:
        peak_season = group_data['Season'].mode().iloc[0]
        count = len(group_data[group_data['Season'] == peak_season])
        total_group = len(group_data)
        percentage = round((count / total_group * 100), 1)
        print(f"{group}: Peak in {peak_season} ({count} cases, {percentage}% of {group} cases)")
