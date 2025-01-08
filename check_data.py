import pandas as pd

try:
    # Read the Excel file and print basic information
    print("Attempting to read Excel file...")
    df = pd.read_excel('PMHP Wellcome Trust screening data_Dec24.xlsx')
    
    print("\nShape of the dataset:")
    print(df.shape)
    
    print("\nFirst 5 column names:")
    print(list(df.columns)[:5])
    
    print("\nFirst 3 rows of data:")
    print(df.iloc[:3, :5])  # Only showing first 5 columns for clarity

except Exception as e:
    print(f"An error occurred: {str(e)}")
