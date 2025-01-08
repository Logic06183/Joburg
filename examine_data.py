import pandas as pd

# Read the Excel file
df = pd.read_excel('PMHP Wellcome Trust screening data_Dec24.xlsx')

# Display column names
print("\nColumn Names:")
print(df.columns.tolist())

# Display first few rows
print("\nFirst few rows of data:")
print(df.head())
