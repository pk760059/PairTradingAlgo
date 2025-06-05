from flask import Flask, jsonify
import pandas as pd
import yfinance as yf
import threading
import time

app = Flask(__name__)

STOCK_PAIRS_FILE = "C:/Users/pramo/Documents/GitHub/PairTrader/Output/New_Stocks_after_threading2.csv"

def fetch_closing_price(stock_ticker, closing_prices, lock, rate_limit=3):
    try:
        time.sleep(rate_limit)

        stock_data = yf.download(stock_ticker, period='5d')
        current_close = stock_data['Adj Close'].iloc[-1]
        previous_close = stock_data['Adj Close'].iloc[-2]

        percentage_change = ((current_close - previous_close) / previous_close) * 100

        # Thread-safe update using a lock
        with lock:
            closing_prices[stock_ticker] = {
                'closing_price': current_close,
                'percentage_change': percentage_change
            }

    except Exception as e:
        print(f"Error fetching data for {stock_ticker}: {e}")
        with lock:
            closing_prices[stock_ticker] = None  

def fetch_closing_prices_threaded(rate_limit=3):
    try:
        stock_pairs_df = pd.read_csv(STOCK_PAIRS_FILE)

        closing_prices = {}
        threads = []
        lock = threading.Lock()

        for index, row in stock_pairs_df.iterrows():
            stock1_ticker = row['Company1 (X)']
            stock2_ticker = row['Company2 (Y)']
            pair_key = f"{stock1_ticker}-{stock2_ticker}"

            closing_prices[pair_key] = {}

            thread1 = threading.Thread(target=fetch_closing_price, args=(stock1_ticker, closing_prices[pair_key], lock, rate_limit))
            thread2 = threading.Thread(target=fetch_closing_price, args=(stock2_ticker, closing_prices[pair_key], lock, rate_limit))
            threads.append(thread1)
            threads.append(thread2)

            thread1.start()
            thread2.start()

        for thread in threads:
            thread.join()

        return closing_prices

    except FileNotFoundError:
        return {"error": "Stock pair file not found"}
    
# (MORE DETAILS SAHIL)
@app.route('/closing_prices', methods=['GET'])
def get_closing_prices():
    closing_prices = fetch_closing_prices_threaded(rate_limit=3)
    return jsonify(closing_prices)

if __name__ == '__main__':
    app.run(debug=True)