import pandas as pd
import matplotlib.pyplot as plt
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
df['date'] = pd.to_datetime(df['date'], format='%d-%b-%y')
df['month'] = df['date'].dt.month
df['month_name'] = df['date'].dt.strftime('%B')

# Count admissions by month
monthly_counts = df['month_name'].value_counts().reindex([
    'December', 'January', 'February',  # Summer
    'March', 'April', 'May',           # Autumn
    'June', 'July', 'August',          # Winter
    'September', 'October', 'November'  # Spring
]).fillna(0)

# Create the visualization
plt.figure(figsize=(15, 10))

# Plot bars
bars = plt.bar(range(len(monthly_counts)), monthly_counts, 
               color=['#f1c40f', '#f1c40f', '#f1c40f',      # Summer
                     '#e67e22', '#e67e22', '#e67e22',      # Autumn
                     '#3498db', '#3498db', '#3498db',      # Winter
                     '#2ecc71', '#2ecc71', '#2ecc71'],     # Spring
               alpha=0.7, edgecolor='#34495e', linewidth=1.5)

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height)}',
             ha='center', va='bottom')

# Add season labels
def add_season_label(start_x, text, color):
    plt.axvspan(start_x - 0.5, start_x + 2.5, alpha=0.1, color=color)
    plt.text(start_x + 1, plt.ylim()[1] * 0.95, text,
             ha='center', va='top', fontsize=12, fontweight='bold')

add_season_label(0, 'Summer', '#f1c40f')
add_season_label(3, 'Autumn', '#e67e22')
add_season_label(6, 'Winter', '#3498db')
add_season_label(9, 'Spring', '#2ecc71')

# Add transition arrows and labels
def add_transition_arrow(x1, x2, y, text):
    plt.annotate('', xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle='<->',
                              color='#34495e',
                              lw=2,
                              shrinkA=0,
                              shrinkB=0))
    plt.text((x1 + x2)/2, y, text,
             ha='center', va='bottom',
             fontsize=10,
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

max_height = max(monthly_counts) * 1.1
arrow_spacings = [0.85, 0.75, 0.65]  # Different heights for arrows

# Add transition arrows
add_transition_arrow(2.5, 3.5, max_height * arrow_spacings[0], 'Summer to Autumn')
add_transition_arrow(5.5, 6.5, max_height * arrow_spacings[1], 'Autumn to Winter')
add_transition_arrow(8.5, 9.5, max_height * arrow_spacings[2], 'Winter to Spring')

# Customize the plot
plt.title('Monthly Admissions with Seasonal Transitions', 
          fontsize=14, pad=20, fontweight='bold')
plt.xlabel('Month', fontsize=12)
plt.ylabel('Number of Admissions', fontsize=12)
plt.xticks(range(len(monthly_counts)), monthly_counts.index, 
           rotation=45, ha='right')

# Add grid for better readability
plt.grid(axis='y', linestyle='--', alpha=0.3)

# Add statistical annotation
from scipy import stats
seasonal_counts = [monthly_counts[0:3].sum(),   # Summer
                  monthly_counts[3:6].sum(),    # Autumn
                  monthly_counts[6:9].sum(),    # Winter
                  monthly_counts[9:12].sum()]   # Spring
expected = np.mean(seasonal_counts)
chi2, p_value = stats.chisquare(seasonal_counts)

stats_text = (f'Statistical Analysis:\n'
             f'Chi-square = {chi2:.3f}\n'
             f'p < {p_value:.3f}')
plt.text(0.02, 0.98, stats_text,
         transform=plt.gca().transAxes,
         verticalalignment='top',
         bbox=dict(boxstyle='round',
                  facecolor='white',
                  alpha=0.8,
                  edgecolor='#34495e'))

plt.tight_layout()
plt.savefig('paper_figures_color/seasonal_transitions.png', 
            dpi=300, bbox_inches='tight')
plt.close()

# Print summary statistics
print("\nSeasonal Transition Analysis:")
print("============================")

seasons = ['Summer', 'Autumn', 'Winter', 'Spring']
for i in range(len(seasons)):
    current_season = seasons[i]
    next_season = seasons[(i + 1) % 4]
    current_count = seasonal_counts[i]
    next_count = seasonal_counts[(i + 1) % 4]
    
    print(f"\n{current_season} to {next_season} Transition:")
    print(f"  {current_season}: {current_count:.0f} cases")
    print(f"  {next_season}: {next_count:.0f} cases")
    print(f"  Change: {next_count - current_count:+.0f} cases")
