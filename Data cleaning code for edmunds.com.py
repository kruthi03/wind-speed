import pandas as pd
import re

# Load CSV file
file_path = "edmunds_used_cars.csv"
df = pd.read_csv(file_path)

# ---- 1. Convert 'Price' to Numeric ----
df['Price'] = df['Price'].replace(r'[\$,]', '', regex=True).astype(float)

# ---- 2. Convert 'Miles Driven' to Numeric ----
df['Miles Driven'] = df['Miles Driven'].replace(r'[,\\smiles]', '', regex=True).astype(float)

# ---- 3. Split 'Car History' ----
if 'Car History' in df.columns:
    df[['Accident History', 'Owner Count', 'Usage Type']] = df['Car History'].str.split(',', expand=True, n=2)

    # Standardize 'Accident History' values
    df['Accident History'] = df['Accident History'].str.strip().fillna('No data')

    # Extract numeric value from 'Owner Count' (e.g., "1 owner" → 1)
    df['Owner Count'] = df['Owner Count'].str.extract(r'(\d+)').astype(float).fillna(0)

    # Standardize 'Usage Type' values
    df['Usage Type'] = df['Usage Type'].str.strip().replace({
        'personal use only': 'Personal',
        'rental vehicle': 'Rental',
        'fleet vehicle': 'Fleet'
    }).fillna('Unknown')

# ---- 4. Extract 'Engine Size' and 'Cylinders' ----
df['Variant'] = df['Variant'].fillna('')  # Ensure no NaN values

# Extract 'Engine Size' separately
df['Engine Size'] = df['Variant'].str.extract(r'(\d+(\.\d+)?)l', expand=False)[0]

# Extract 'Cylinders' separately
df['Cylinders'] = df['Variant'].str.extract(r'(\d+)cyl', expand=False)

# Extract 'Transmission' type (manual/automatic)
df['Transmission'] = df['Variant'].str.extract(r'(automatic|manual)', expand=False)

# Convert 'Engine Size' and 'Cylinders' to numeric values
df['Engine Size'] = pd.to_numeric(df['Engine Size'], errors='coerce')
df['Cylinders'] = pd.to_numeric(df['Cylinders'], errors='coerce')

# ---- 5. Extract Dealer and Distance from 'Location' ----
df['Dealer'] = df['Location'].str.extract(r'^(.*?)\s\(', expand=False)
df['Distance (mi)'] = df['Location'].str.extract(r'(\d+) mi away', expand=False).astype(float)

# ---- 6. Convert 'Below Market Price' to Numeric ----
df['Below Market Price'] = df['Below Market Price'].replace(r'[\$, below market]', '', regex=True).astype(float).fillna(0)

# ---- 7. Drop Unnecessary Columns ----
columns_to_drop = ['Car History', 'Variant', 'Location', 'Image URL']
df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)

# ---- 8. Save Cleaned Data ----
cleaned_file_path = "edmunds_used_cars_cleaned.csv"
df.to_csv(cleaned_file_path, index=False)

print(f"Cleaned CSV file saved to: {cleaned_file_path}")
