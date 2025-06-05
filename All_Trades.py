import os
import pandas as pd
from multiprocessing import Pool

# Get the current running folder
current_folder = os.getcwd()

# Define paths
data_path = os.path.join(current_folder, 'Data', 'BacktestData', 'Sectorwise')
output_path = os.path.join(current_folder, 'Output')
os.makedirs(output_path, exist_ok=True)

# Function to process each file
def process_file(sector_folder, csv_file):
    print(f"Processing file: {csv_file}")
    
    # Extract stock names from the filename
    stock1, stock2 = csv_file.replace('.csv', '').split('_')
    
    # Read the CSV file
    csv_path = os.path.join(sector_folder, csv_file)
    df = pd.read_csv(csv_path)
    
    # Clean up column names by stripping whitespace
    df.columns = df.columns.str.strip()
    
    # Check if the 'Trades' column exists
    if 'Trades' not in df.columns:
        print(f"'Trades' column not found in {csv_file}. Skipping file.")
        return pd.DataFrame()
    
    # Initialize variables to track trade status
    trade_opened = False
    start_date = None

    # Add 'start date' and 'end date' columns to the DataFrame
    df['start date'] = ''
    df['end date'] = ''
    df_dates = df
    # Track trades to fill 'start date' and 'end date' columns
    start_date = None
    end_date = None
    trade_number = 0
    for i in range(len(df_dates)):
        signal = df_dates.at[i, 'Signal']
        if signal in [1, -1] and not trade_opened:
            # Start a new trade
            trade_opened = True
            start_date = df_dates.at[i, 'Dates']
        elif signal == 0 and trade_opened:
            # End the current trade
            end_date = df_dates.at[i, 'Dates']
            trade_opened = False
            #here append start date and end date in df
            df_dates.at[trade_number, 'start date'] = start_date
            df_dates.at[trade_number, 'end date'] = end_date
            trade_number += 1

    # Determine the number of valid trades
    trades_count = df['Trades'].notna().sum()
    print(f"Number of trades determined: {trades_count}")

    # Slice the DataFrame to include only the rows up to the number of trades
    df = df.iloc[:trades_count]
    
    # Column name to check
    column_name = f'Effective Investment of {stock2}.NS Y'

    # Check if the column exists in the DataFrame
    if column_name in df.columns:
        print(f"The column '{column_name}' is present in the DataFrame.")
    else:
        print(f"The column '{column_name}' is not present in the DataFrame. swapping stock names.")
        stock1, stock2 = stock2, stock1#swapping stocks



    # Generalized columns
    columns_to_keep = [
        'Trades', 'Investments', 'Net Investments',
        f'Effective Margin of {stock1}.NS X', f'Effective Margin of {stock2}.NS Y', 'Trade Length',
        'Percentage Return', 'Profit', 'Net Percentage Return',
        'Long Profit', 'Short Profit',
        f'Effective Investment of {stock1}.NS X', f'Effective Investment of {stock2}.NS Y', 'Multiplier X',
        'Multiplier Y'
    ]
    
    # Check if columns exist before selecting them
    existing_columns = [col for col in columns_to_keep if col in df.columns]
    print(existing_columns)
    df = df[existing_columns]

    # Replace specific column names with generic ones
    df.columns = df.columns.str.replace(f'Effective Margin of {stock1}.NS X', 'Effective Margin of X', regex=False)
    df.columns = df.columns.str.replace(f'Effective Margin of {stock2}.NS Y', 'Effective Margin of Y', regex=False)
    df.columns = df.columns.str.replace(f'Effective Investment of {stock1}.NS X', 'Effective Investment of X', regex=False)
    df.columns = df.columns.str.replace(f'Effective Investment of {stock2}.NS Y', 'Effective Investment of Y', regex=False)


    # Add 'stock X' and 'stock Y' columns
    df['stock X'] = stock1
    df['stock Y'] = stock2
    # Add 'start date' and 'end date' columns from df_dates
    df['start date'] = df_dates.get('start date', '')
    df['end date'] = df_dates.get('end date', '')

    # Move 'start date', 'end date', 'stock X', and 'stock Y' to the beginning
    cols_to_move = ['Trades','start date', 'end date', 'stock X', 'stock Y']
    remaining_cols = [col for col in df.columns if col not in cols_to_move]
    df = df[cols_to_move + remaining_cols]

    # Remove rows where 'Trades' column has no values (empty or NaN)
    df = df[df['Trades'].notna() & (df['Trades'] != '')]
    return df

def main():
    # Get list of sector folders
    sector_folders = [os.path.join(data_path, folder) for folder in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, folder))]
    
    # Initialize an empty list to store DataFrames
    all_trades_dfs = []

    with Pool() as pool:
        # Create tasks for each file in each sector folder
        tasks = [(sector_folder, csv_file) 
                 for sector_folder in sector_folders 
                 for csv_file in os.listdir(sector_folder) 
                 if csv_file.endswith('.csv')]
        
        # Process files in parallel
        results = pool.starmap(process_file, tasks)
        
        # Collect all DataFrames
        all_trades_dfs = [df for df in results if not df.empty]
    
    # Concatenate all DataFrames
    all_trades_df = pd.concat(all_trades_dfs, ignore_index=True)

    # Save the result to a new CSV file in the Output folder
    output_file = os.path.join(output_path, 'all_trades.csv')
    all_trades_df.to_csv(output_file, index=False)

    print(f"All trades have been processed and saved to {output_file}")

if __name__ == "__main__":
    main()
