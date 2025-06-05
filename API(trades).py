import os
import pandas as pd
import yfinance as yf
from flask import Flask, jsonify
import threading

app = Flask(__name__)

# File paths
data_directory = r'C:\\Users\\pramo\\Documents\\GitHub\\PairTrader\\Data\\FinalBacktestData'
stock_pairs_file = r'C:\\Users\\pramo\\Documents\\GitHub\\PairTrader\\Output\\New_Stocks_after_threading2.csv'

result_lock = threading.Lock()

stock_pair_df = pd.read_csv(stock_pairs_file)

def load_stock_pairs():
    stock_pairs_df = pd.read_csv(stock_pairs_file)
    stock_pairs = list(zip(stock_pairs_df['Company1 (X)'], stock_pairs_df['Company2 (Y)']))
    return stock_pairs

def process_stock_pair(stock_pair_list, results):

    stock1_name = stock_pair_list[0].replace(".NS", "")
    stock2_name = stock_pair_list[1].replace(".NS", "")
    csv_file = f"{stock1_name}_{stock2_name}.csv"

    stock_pair_data = os.listdir(data_directory)
    if csv_file in stock_pair_data:
        
        data_path = os.path.join(data_directory, csv_file)
        df = pd.read_csv(data_path)

        # (POSSIBLE ERROR SPOT)   Fetch the first 6 rows of data bcoz unordered
        trades = df['Trades'][:6].tolist()
        investment = df['Investments'][:6].tolist()
        net_invest = df['Net Investments'][:6].tolist()
        trade_length = df['Trade Length'][:6].tolist()
        percentage_return = df['Percentage Return'][:6].tolist()
        profit = df['Profit'][:6].tolist()
    
        trades = [val for val in trades if pd.notna(val)]
        investment = [val for val in investment if pd.notna(val)]
        net_invest = [val for val in net_invest if pd.notna(val)]
        trade_length = [val for val in trade_length if pd.notna(val)]
        percentage_return = [val for val in percentage_return if pd.notna(val)]
        profit = [val for val in profit if pd.notna(val)]

        result_dict = {
            trades[i]: {
                'Investment': investment[i],
                'Net Investment': net_invest[i],
                'Trade Length': trade_length[i],
                'Percentage Return': percentage_return[i],
                'Profit': profit[i]
            }
            for i in range(len(trades))
        }

        with result_lock:
            results.append({
                f'{stock1_name}-{stock2_name}': {
                    'Trading Details': result_dict
                }
            })

    else:
        with result_lock:
            results.append({
                f'{stock1_name}-{stock2_name}': {
                    'Trading Details': 'Data Not available'
                }
            })

#  (CHANGES FOR SAHIL) API route to get stock pair data
@app.route('/trades', methods=['GET'])
def get_stock_pair_data():
    stock_pair_list = []
    for index, row in stock_pair_df.iterrows():
        stock1_ticker = row['Company1 (X)']
        stock2_ticker = row['Company2 (Y)']
        stock_pair = [stock2_ticker, stock1_ticker]
        stock_pair_list.append(stock_pair)
    stock_pairs = load_stock_pairs()
    results = []  
    threads = []

    for stock_pair in stock_pair_list:
        thread = threading.Thread(target=process_stock_pair, args=(stock_pair, results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
