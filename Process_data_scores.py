import pandas as pd

def calculate_number_of_days_cointegrated(input_df):
    """
    Calculate the number of days cointegrated.
    """
    return (input_df['Coint'] < 0.1).sum()

def calculate_average_trade_time(input_df):
    """
    Calculate the average trade time and the total number of trades.
    """
    trade_lengths = []
    for value in input_df['Trade Length']:
        if pd.isnull(value):
            break
        trade_lengths.append(pd.to_numeric(value, errors='coerce'))
    total_trade_time = sum(trade_lengths)
    total_trades = len(trade_lengths)
    return total_trade_time / total_trades if total_trades > 0 else 0, total_trades

def calculate_positive_past_trades_and_avg_returns(input_df):
    """
    Calculate the number of positive past trades and the average returns.
    """
    profits = pd.to_numeric(input_df['Profit'], errors='coerce')
    positive_trades = (profits > 0).sum()
    total_returns = profits.sum()
    total_trades = profits.count()
    avg_returns = total_returns / total_trades if total_trades > 0 else 0
    return positive_trades, total_trades, avg_returns

def calculate_average_percentage_returns(input_df):
    """
    Calculate the average percentage returns.
    """
    percentage_returns = pd.to_numeric(input_df['Percentage Return'], errors='coerce')
    total_percentage_returns = percentage_returns.sum()
    total_trades = percentage_returns.count()
    avg_percentage_returns = total_percentage_returns / total_trades if total_trades > 0 else 0
    return avg_percentage_returns

def process_stock_data(input_filepath, output_filepath, stock1, stock2, sector):
    """
    Main function to process stock data and update the output CSV file.

    Parameters:
    input_filepath (str): Path to the input CSV file.
    output_filepath (str): Path to the output CSV file.
    stock1 (str): Stock 1 name.
    stock2 (str): Stock 2 name.
    sector (str): Sector name.
    """
    # Append '.NS' to stock1 and stock2
    stock1 = stock1 + '.NS'
    stock2 = stock2 + '.NS'

    # Read the input CSV file into a DataFrame
    input_df = pd.read_csv(input_filepath)

    # Read the output CSV file into a DataFrame
    output_df = pd.read_csv(output_filepath)

    # Define the required columns
    required_columns = [
        'Number of Days Cointegrated', 
        'Average Trade time', 
        'Positive past Trades', 
        'Total Past trades', 
        'Average returns',
        'Average Percentage Returns'
    ]

    # Check if required columns exist in the output file, if not create them
    for col in required_columns:
        if col not in output_df.columns:
            output_df[col] = 0

    # Calculate the required values
    num_days_cointegrated = calculate_number_of_days_cointegrated(input_df)
    avg_trade_time, total_trades = calculate_average_trade_time(input_df)
    positive_trades, total_trades, avg_returns = calculate_positive_past_trades_and_avg_returns(input_df)
    avg_percentage_returns = calculate_average_percentage_returns(input_df)

    # Find the appropriate row in the output DataFrame
    row_index = output_df[(output_df['Company2 (Y)'] == stock2) & 
                          (output_df['Company1 (X)'] == stock1) & 
                          (output_df['Sector'] == sector)].index

    # Update the row with the calculated values
    if len(row_index) > 0:
        row_index = row_index[0]
        output_df.at[row_index, 'Number of Days Cointegrated'] = num_days_cointegrated
        output_df.at[row_index, 'Average Trade time'] = avg_trade_time
        output_df.at[row_index, 'Positive past Trades'] = positive_trades
        output_df.at[row_index, 'Total Past trades'] = total_trades
        output_df.at[row_index, 'Average returns'] = avg_returns
        output_df.at[row_index, 'Average Percentage Returns'] = avg_percentage_returns

    # Save the updated output file
    output_df.to_csv(output_filepath, index=False)

# Example usage
# process_stock_data(
#     r"C:\Users\arshm\OneDrive\Desktop\Py\Pair_T\PairTrader\Data\BacktestData\Sectorwise\2-Wheeler\TVSMOTOR_BAJAJ-AUTO.csv",
#     r"C:\Users\arshm\OneDrive\Desktop\Py\Pair_T\PairTrader\Output\stocks_pairs.csv",
#     "BAJAJ-AUTO", "TVSMOTOR", "2-Wheeler"
# )
