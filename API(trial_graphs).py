from flask import Flask, jsonify, send_from_directory
import pandas as pd
import yfinance as yf
import os
import base64

app = Flask(__name__)

# File paths
STOCK_PAIRS_FILE = "C:/Users/pramo/Documents/GitHub/PairTrader/Output/New_Stocks.csv"
IMAGE_FOLDER = "C:/Users/pramo/Documents/GitHub/PairTrader/Data/Graph"

def fetch_closing_prices():
    try:
        stock_pairs_df = pd.read_csv(STOCK_PAIRS_FILE)

        closing_prices = []

        for index, row in stock_pairs_df.iterrows():
            stock1_ticker = row['Company1 (X)']
            stock2_ticker = row['Company2 (Y)']
            stock_pair_image = f"{stock2_ticker[:-3]}_{stock1_ticker[:-3]}.png"

            try:
                stock1_data = yf.download(stock1_ticker, period='1d')
                stock2_data = yf.download(stock2_ticker, period='1d')

                stock1_closing_price = stock1_data['Adj Close'].iloc[-1]
                stock2_closing_price = stock2_data['Adj Close'].iloc[-1]

                pair_data = {
                    'stock1': stock1_ticker,
                    'stock1_closing_price': stock1_closing_price,
                    'stock2': stock2_ticker,
                    'stock2_closing_price': stock2_closing_price,
                }

                if os.path.exists(os.path.join(IMAGE_FOLDER, stock_pair_image)):
                    with open(os.path.join(IMAGE_FOLDER, stock_pair_image), "rb") as image_file:
                        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                        pair_data['image'] = encoded_image
                else:
                    pair_data['image'] = None

                closing_prices.append(pair_data)

            except Exception as e:
                print(f"Error fetching data for {stock2_ticker}-{stock1_ticker}: {e}")

        return closing_prices	

    except FileNotFoundError:
        return {"error": "Stock pair file not found"}

@app.route('/closing_prices', methods=['GET'])
def get_closing_prices():
    closing_prices = fetch_closing_prices()
    return jsonify(closing_prices)

if __name__ == '__main__':
    app.run(debug=True)

print(get_closing_prices())