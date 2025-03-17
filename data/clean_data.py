import pandas as pd

# Load the raw crime dataset
file_path = "data/RCD06.20250317132007.csv"
df = pd.read_csv(file_path)

# Display the first few rows of the raw dataset
print("Raw Data Preview:")
print(df.head())

# Drop any completely empty rows
df.dropna(how="all", inplace=True)

# Fill missing values in numeric columns with 0
numeric_cols = df.select_dtypes(include=['number']).columns
df[numeric_cols] = df[numeric_cols].fillna(0)

# Standardize column names (remove spaces & lowercase)
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Convert 'year' column to integer if it exists
if 'year' in df.columns:
    df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(0).astype(int)

# Remove any duplicate rows
df.drop_duplicates(inplace=True)

# Save cleaned data
cleaned_file_path = "data/cleaned_crime_data.csv"
df.to_csv(cleaned_file_path, index=False)

print(f"\n✅ Data cleaning complete! Cleaned file saved at: {cleaned_file_path}")

# Show summary of cleaned data
print("\n📊 Cleaned Data Preview:")
print(df.head())
print("\n📌 Dataset Summary:")
print(df.info())
