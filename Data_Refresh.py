import os
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

# Change this folder path to the Yt stock data folder
FOLDER_PATH = r'C:\Users\pramo\Documents\GitHub\PairTrader\Data\Yt Stock Data'

# Create a dictionary of file paths
file_dict = {
    entry.name: os.path.join(FOLDER_PATH, entry.name)
    for entry in os.scandir(FOLDER_PATH)
    if entry.is_file()
}


def extract_namespaces(filename):
    """
    Extracts namespaces (stock names) from a filename.
    """
    parts = filename.split("_")
    return parts[:2] if len(parts) > 2 else parts[:1]

def get_last_date(csv_path):
    """
    Retrieves the latest date from the 'Date' column of the CSV file.
    Handles cases where the 'Date' column is missing or improperly formatted.
    """
    try:
        # Read the CSV file
        data = pd.read_csv(csv_path)
        
        # Check if the 'Date' column exists
        if "Date" not in data.columns:
            print(f"Error: 'Date' column not found in {csv_path}. Skipping this file.")
            return None
        
        # Convert the 'Date' column to datetime
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce").dt.date
        
        # Drop rows with invalid dates
        data = data.dropna(subset=["Date"])
        
        # Return the latest date
        return data["Date"].max()
    except Exception as e:
        print(f"Error processing {csv_path}: {e}")
        return None

def stockstore(stock1, stock2, start_date, end_date):
    """
    Downloads and stores stock closing data from Yahoo Finance.
    """
    try:
        data = yf.download(f"{stock1} {stock2}", start=start_date, end=end_date)["Close"]
        data = data.fillna(method="ffill").fillna(method="bfill")
        return data
    except Exception as e:
        print(f"Error fetching data for {stock1}, {stock2} between {start_date} and {end_date}: {e}")
        return pd.DataFrame()


def append_rows_to_csv(csv_path, new_data):
    """
    Appends rows to an existing CSV file, ensuring the date format is YYYY-MM-DD.
    """
    try:
        # Read existing data if the file exists
        existing_data = pd.read_csv(csv_path)
    except FileNotFoundError:
        existing_data = pd.DataFrame()

    # Ensure the "Date" column is formatted as 'YYYY-MM-DD'
    new_data["Date"] = pd.to_datetime(new_data["Date"]).dt.strftime('%Y-%m-%d')

    # Combine new data with existing data
    updated_data = pd.concat([existing_data, new_data], ignore_index=True)

    # Write the updated data back to the CSV
    updated_data.to_csv(csv_path, index=False, header=False)
    print(f"Rows successfully appended to {csv_path}")


def update_stock_data(filename, csv_path):
    """
    Updates stock data by downloading missing dates and appending them to the CSV.
    """
    last_date = get_last_date(csv_path)
    if not last_date:
        print(f"No existing data found for {filename}.")
        return

    next_date = last_date + timedelta(days=1)
    today = datetime.now().strftime('%Y-%m-%d')

    stocks = extract_namespaces(filename)
    if len(stocks) < 2:
        print(f"Invalid filename format for {filename}. Skipping.")
        return

    new_data = stockstore(stocks[0], stocks[1], start_date=next_date.strftime('%Y-%m-%d'), end_date=today)
    if new_data.empty:
        print(f"No new data found for {stocks}. Possibly up-to-date or holiday.")
        return

    new_data = new_data.reset_index()
    new_data = new_data.rename(columns={'index': 'Date'})
    new_data["Date"] = pd.to_datetime(new_data["Date"]).dt.strftime('%Y-%m-%d')
    append_rows_to_csv(csv_path, new_data)
    print(f"Data successfully updated for {stocks} in {csv_path}.")


# Main loop to update all files
for filename, filepath in file_dict.items():
    update_stock_data(filename, filepath)
