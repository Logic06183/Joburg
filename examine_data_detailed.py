import pandas as pd

# Read the Excel file
df = pd.read_excel('PMHP Wellcome Trust screening data_Dec24.xlsx')

# Display information about the dataframe
print("DataFrame Info:")
print(df.info())

print("\nFirst 10 rows:")
print(df.head(10))

print("\nColumn names:")
print(df.columns.tolist()[:20])  # First 20 columns

print("\nData types of columns:")
for col in df.columns:
    print(f"{col}: {df[col].dtype}")

print("\nSample of non-null values in each column:")
for col in df.columns:
    non_null_values = df[col].dropna().head(3)
    if not non_null_values.empty:
        print(f"\n{col}:")
        print(non_null_values)
