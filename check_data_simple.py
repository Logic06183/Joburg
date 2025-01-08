import pandas as pd

# Read the Excel file
df = pd.read_excel('PMHP Wellcome Trust screening data_Dec24.xlsx')

# Get only the relevant columns
relevant_cols = ['Unnamed: 0', 'Screen offered', 'Screen decline', 'Screened', 'Interrupted']
df = df[relevant_cols]

print("First 10 rows of data:")
print(df.head(10))

print("\nData types:")
print(df.dtypes)
