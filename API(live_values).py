from flask import Flask, jsonify, request
import pandas as pd
import yfinance as yf
import time

app = Flask(__name__)

STOCK_PAIRS_FILE = "C:/Users/pramo/Documents/GitHub/PairTrader/Output/New_Stocks_after_threading2.csv"

def fetch_closing_prices():

    try:
        # Load stuff from the CSV file
        stock_pairs_df = pd.read_csv(STOCK_PAIRS_FILE)

        closing_prices = {}

        for index, row in stock_pairs_df.iterrows():
            stock1_ticker = row['Company1 (X)']
            stock2_ticker = row['Company2 (Y)']
            corr = row['Correlation']
            ratio = row['ratio']

            try:
                stock1_data = yf.download(stock1_ticker, period='1d')
                stock2_data = yf.download(stock2_ticker, period='1d')

                stock1_closing_price = stock1_data['Adj Close'].iloc[-1]
                stock2_closing_price = stock2_data['Adj Close'].iloc[-1]

                closing_prices[f"{stock1_ticker}-{stock2_ticker}"] = {
                    f'{stock1_ticker}': stock1_closing_price,
                    f'{stock2_ticker}': stock2_closing_price,
                    'correlation': corr,
                    'ratio': ratio
                }

                # Introduce a delay to avoid rate limiting
                time.sleep(1)  # Adjust the delay as needed

            except Exception as e:
                print(f"Error fetching data for {stock1_ticker}-{stock2_ticker}: {e}")

        return closing_prices	

    except FileNotFoundError:
        return {"error": "Stock pair file not found"}

@app.route('/closing_prices', methods=['GET'])
def get_closing_prices():
    closing_prices = fetch_closing_prices()
    return jsonify(closing_prices)

if __name__ == '__main__':
    app.run(debug=True)