import pandas as pd
import os
from itertools import combinations

# Input and output directories
input_folder = 'Input'
output_folder = 'Output'
input_file = os.path.join(input_folder, 'FNO.csv')
output_file = os.path.join(output_folder, 'stocks_pairs.csv')

# Read the CSV file
df = pd.read_csv(input_file)

# Select relevant columns
df = df[['SYMBOLS', 'Sector']]

# Drop rows with missing values in SYMBOLS or Sector
df = df.dropna(subset=['SYMBOLS', 'Sector'])

# Strip trailing spaces from the Sector column
df['Sector'] = df['Sector'].str.rstrip()

# Create pairs of stocks within the same sector
pairs = []
for sector in df['Sector'].unique():
    sector_df = df[df['Sector'] == sector]
    for (idx1, row1), (idx2, row2) in combinations(sector_df.iterrows(), 2):
        pair = {
            'Company2 (Y)': row1['SYMBOLS'],
            'Company1 (X)': row2['SYMBOLS'],
            'Sector': sector,
        }
        pairs.append(pair)

# Convert pairs list to DataFrame
pairs_df = pd.DataFrame(pairs)

# Sort pairs by Sector
pairs_df = pairs_df.sort_values(by='Sector')

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# Save to CSV
pairs_df.to_csv(output_file)

print(f'Pairs of stocks have been saved to {output_file}')
