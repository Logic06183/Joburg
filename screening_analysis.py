import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import calendar

# Read the Excel file
df = pd.read_excel('PMHP Wellcome Trust screening data_Dec24.xlsx')

def perform_analysis():
    # Display basic information about the dataset
    print("\nDataset Info:")
    print(df.info())
    
    print("\nSummary Statistics:")
    print(df.describe())
    
    # Check for missing values
    print("\nMissing Values:")
    print(df.isnull().sum())
    
    # Create visualizations directory if it doesn't exist
    import os
    if not os.path.exists('visualizations'):
        os.makedirs('visualizations')
    
    # Create various visualizations based on the data
    
    # 1. Time series of admissions
    plt.figure(figsize=(12, 6))
    df['Date'].value_counts().sort_index().plot(kind='line')
    plt.title('Screening Admissions Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Admissions')
    plt.tight_layout()
    plt.savefig('visualizations/admissions_over_time.png')
    plt.close()
    
    # 2. Distribution of key variables (modify column names as needed)
    for column in df.select_dtypes(include=['object']).columns:
        plt.figure(figsize=(10, 6))
        df[column].value_counts().plot(kind='bar')
        plt.title(f'Distribution of {column}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'visualizations/{column}_distribution.png')
        plt.close()
    
    # 3. Seasonal analysis if date information is available
    if 'Date' in df.columns:
        df['Month'] = df['Date'].dt.month
        df['Season'] = df['Month'].map(lambda x: 'Summer' if x in [12,1,2] else
                                              'Autumn' if x in [3,4,5] else
                                              'Winter' if x in [6,7,8] else 'Spring')
        
        plt.figure(figsize=(10, 6))
        df['Season'].value_counts().plot(kind='bar')
        plt.title('Admissions by Season')
        plt.xlabel('Season')
        plt.ylabel('Number of Admissions')
        plt.tight_layout()
        plt.savefig('visualizations/seasonal_distribution.png')
        plt.close()

if __name__ == "__main__":
    perform_analysis()
    print("\nAnalysis complete. Visualizations have been saved to the 'visualizations' folder.")
