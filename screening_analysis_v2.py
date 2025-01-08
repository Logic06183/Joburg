import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style for better-looking plots
plt.style.use('seaborn')

# Read the Excel file
df = pd.read_excel('PMHP Wellcome Trust screening data_Dec24.xlsx')

# Clean up the dataframe by removing empty columns
df = df.loc[:, ~df.columns.str.contains('^Unnamed: [2-9]|^Unnamed: [1-9][0-9]')]

def create_visualizations():
    # Create visualizations directory if it doesn't exist
    if not os.path.exists('visualizations'):
        os.makedirs('visualizations')
    
    # 1. Time Series Plot of Screening Metrics
    plt.figure(figsize=(12, 6))
    metrics = ['Screen offered', 'Screen decline', 'Screened', 'Interrupted']
    for metric in metrics:
        if metric in df.columns:
            plt.plot(df['Unnamed: 0'], df[metric], label=metric, marker='o')
    
    plt.title('Screening Metrics Over Time')
    plt.xlabel('Month')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig('visualizations/screening_metrics_time_series.png')
    plt.close()

    # 2. Monthly Averages
    monthly_data = df.copy()
    monthly_data['Month'] = pd.to_datetime(df['Unnamed: 0'], format='%b \'%y').dt.month
    
    plt.figure(figsize=(10, 6))
    monthly_means = monthly_data.groupby('Month')[metrics].mean()
    monthly_means.plot(kind='bar')
    plt.title('Average Monthly Screening Metrics')
    plt.xlabel('Month')
    plt.ylabel('Average Count')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('visualizations/monthly_averages.png')
    plt.close()

    # 3. Screening Success Rate
    if all(col in df.columns for col in ['Screen offered', 'Screened']):
        df['Success Rate'] = (df['Screened'] / df['Screen offered'] * 100).round(2)
        
        plt.figure(figsize=(12, 6))
        plt.plot(df['Unnamed: 0'], df['Success Rate'], marker='o')
        plt.title('Screening Success Rate Over Time')
        plt.xlabel('Month')
        plt.ylabel('Success Rate (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('visualizations/success_rate.png')
        plt.close()

    # Print summary statistics
    print("\nSummary Statistics:")
    print(df[metrics].describe())
    
    # Calculate and print key findings
    print("\nKey Findings:")
    for metric in metrics:
        if metric in df.columns:
            total = df[metric].sum()
            avg = df[metric].mean()
            print(f"\n{metric}:")
            print(f"Total: {total:.0f}")
            print(f"Monthly Average: {avg:.2f}")

if __name__ == "__main__":
    create_visualizations()
    print("\nAnalysis complete. Visualizations have been saved to the 'visualizations' folder.")
