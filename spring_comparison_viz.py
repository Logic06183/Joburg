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

# Define spring months (September, October, November)
spring_months = [9, 10, 11]
df['is_spring'] = df['month'].isin(spring_months)

# Calculate average cases per month for spring and rest of year
spring_count = df[df['is_spring']].shape[0]
non_spring_count = df[~df['is_spring']].shape[0]

spring_months_count = 3  # Sep, Oct, Nov
non_spring_months_count = 9  # Rest of the year

spring_avg = spring_count / spring_months_count
non_spring_avg = non_spring_count / non_spring_months_count

# Create the plot
plt.figure(figsize=(8, 6))

# Plot bars
bars = plt.bar([0, 1], [spring_avg, non_spring_avg],
               color=['#ff7f50', '#4169e1'],  # Coral for spring, Royal Blue for rest of year
               width=0.6)

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f}',
             ha='center', va='bottom')

# Customize the plot
plt.title('Bara Mental Health Cases\nper Month', 
          fontsize=12, pad=20)
plt.xticks([0, 1], ['Spring', 'Rest of Year'])
plt.ylabel('Average Cases per Month')

# Add grid
plt.grid(axis='y', linestyle='-', alpha=0.2)

# Add source and difference information
plt.figtext(0.1, 0.02, 'Source: CHBAH Maternity 2023-2024\nSpring diff: 3.0',
            fontsize=8, ha='left')

plt.tight_layout()

# Save the plot
plt.savefig('paper_figures_color/spring_comparison.png', 
            dpi=300, bbox_inches='tight')
plt.close()

# Print statistics
print("\nSpring vs Rest of Year Analysis:")
print("================================")
print(f"Spring (SON) average: {spring_avg:.1f} cases per month")
print(f"Rest of Year average: {non_spring_avg:.1f} cases per month")
print(f"Difference: {spring_avg - non_spring_avg:+.1f} cases per month")
print(f"\nTotal cases in Spring: {spring_count}")
print(f"Total cases in Rest of Year: {non_spring_count}")
print(f"Total cases: {len(df)}")
