import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set the style for publication-quality figures
plt.style.use('seaborn-v0_8-paper')
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['figure.titlesize'] = 14

# Load and prepare the data
data = pd.read_excel("paper_figures_color/datasets/10122024 mental health issues in obstetrics final final.xlsx")

# Create Season column based on date
data['Month'] = pd.to_datetime(data['date']).dt.month
season_map = {
    12: 'Summer', 1: 'Summer', 2: 'Summer',
    3: 'Autumn', 4: 'Autumn', 5: 'Autumn',
    6: 'Winter', 7: 'Winter', 8: 'Winter',
    9: 'Spring', 10: 'Spring', 11: 'Spring'
}
data['Season'] = data['Month'].map(season_map)

# Create a figure with two subplots side by side
fig = plt.figure(figsize=(15, 7))
gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.2], wspace=0.4)

# First subplot: Distribution by Season
ax1 = fig.add_subplot(gs[0])

# Calculate seasonal counts
data['Season'] = pd.Categorical(data['Season'], categories=['Summer', 'Autumn', 'Winter', 'Spring'])
seasonal_counts = data.groupby(['Season', 'diagnosis']).size().unstack(fill_value=0)

# Custom color palette
colors = sns.color_palette("husl", n_colors=len(seasonal_counts.columns))

# Plot stacked bar chart
seasonal_counts.plot(kind='bar', stacked=True, ax=ax1, color=colors)
ax1.set_title('Distribution of Diagnoses by Season', pad=20, fontweight='bold')
ax1.set_xlabel('Season')
ax1.set_ylabel('Number of Cases')
ax1.tick_params(axis='x', rotation=45)
ax1.legend(title='Diagnosis', bbox_to_anchor=(1.05, 1), loc='upper left', 
          fontsize=8, title_fontsize=9)

# Add grid for better readability
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# Second subplot: Heatmap
ax2 = fig.add_subplot(gs[1])

# Create month names for better readability
month_names = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}
data['Month_Name'] = data['Month'].map(month_names)

# Create monthly diagnosis counts
monthly_counts = data.groupby(['Month_Name', 'diagnosis']).size().unstack(fill_value=0)
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']
monthly_counts = monthly_counts.reindex(month_order)

# Create heatmap with improved styling
sns.heatmap(monthly_counts, 
            cmap='YlOrRd',
            ax=ax2, 
            cbar_kws={'label': 'Number of Cases', 'orientation': 'horizontal'},
            annot=True,  # Add number annotations
            fmt='.0f',   # Format as integer without decimal places
            square=True, # Make cells square
            linewidths=0.5)

ax2.set_title('Monthly Distribution of Diagnoses', pad=20, fontweight='bold')
ax2.set_xlabel('Diagnosis')
ax2.set_ylabel('Month')
plt.xticks(rotation=45, ha='right')

# Add overall figure title
fig.suptitle('Seasonal Analysis of Mental Health Diagnoses\nat Rahima Moosa Mother and Child Hospital', 
             y=1.05, fontweight='bold')

# Add source note
fig.text(0.99, -0.05, 
         'Source: Rahima Moosa Mother and Child Hospital, 2023-2024',
         fontsize=8, style='italic', ha='right')

# Adjust layout
plt.tight_layout()

# Save the figure
plt.savefig('seasonal_analysis_improved.png', dpi=300, bbox_inches='tight')
plt.close()
