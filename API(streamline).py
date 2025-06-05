import yfinance as yf
import datetime
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
from scipy import stats
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify, Response, json
import pandas as pd
import os
from collections import OrderedDict
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=2 * 365)

data = pd.read_csv(r"C:\Users\pramo\Documents\GitHub\PairTrader\Input\FNO_LIST.csv")
grouped = data.groupby('Sector')
resultList = []

for key, group in grouped:
    for b, g in combinations(group['SYMBOLS'].tolist(), 2):
        resultList.append([b, g, key])

resultList.sort()
total_list = resultList

data_directory = r'C:\\Users\\pramo\\Documents\\GitHub\\PairTrader\\Data\\FinalBacktestData'
image_directory = r'C:\\Users\\pramo\\Documents\\GitHub\\PairTrader\\Data\\Graph'
stock_pairs_file = r'C:\\Users\\pramo\\Documents\\GitHub\\PairTrader\\Output\\New_Stocks_after_threading2.csv'

def cheg_list(total_list):
    rlist = []
    for all_list in total_list:
        s1 = all_list[0]
        s2 = all_list[1]
        file_path_1 = os.path.join(r"C:\Users\pramo\Documents\GitHub\PairTrader\Data\Yt Stock Data", f"{s1}_{s2}_StoredData.csv")
        file_path_2 = os.path.join(r"C:\Users\pramo\Documents\GitHub\PairTrader\Data\Yt Stock Data", f"{s2}_{s1}_StoredData.csv")
        
        if os.path.exists(file_path_1):
            df = pd.read_csv(file_path_1)
        elif os.path.exists(file_path_2):
            df = pd.read_csv(file_path_2)
        else:
            continue
        
        cor = df[s1].corr(df[s2])
        if cor > 0.84:
            rlist.append(all_list)
    return rlist

mliys = cheg_list(total_list)

def StockCheck(mlist, results):
    stock1 = mlist[0]
    stock2 = mlist[1]
    
    file_path_1 = os.path.join(r"C:\Users\pramo\Documents\GitHub\PairTrader\Data\Yt Stock Data", f"{stock1}_{stock2}_StoredData.csv")
    file_path_2 = os.path.join(r"C:\Users\pramo\Documents\GitHub\PairTrader\Data\Yt Stock Data", f"{stock2}_{stock1}_StoredData.csv")

    if os.path.exists(file_path_1):
        data = pd.read_csv(file_path_1)
    elif os.path.exists(file_path_2):
        data = pd.read_csv(file_path_2)
    else:
        return

    last_row = data.iloc[-1]
    stock1_price = last_row[stock1]
    stock2_price = last_row[stock2]
    
    try:
        data['ratio'] = data[stock1] / data[stock2]
        cor = data[stock1].corr(data[stock2])

        if cor < 0.88:
            return

        xdata = data[stock1]
        ydata = data[stock2]
        latestx = xdata.iloc[-1]
        latesty = ydata.iloc[-1]

        result_xy = stats.linregress(xdata, ydata)
        stder_xy = result_xy.intercept_stderr
        result_yx = stats.linregress(ydata, xdata)
        stder_yx = result_yx.intercept_stderr

        model_xy = sm.OLS(ydata, sm.add_constant(xdata)).fit()
        influence_xy = model_xy.get_influence()
        residualerror_xy = influence_xy.resid.std()  # Error for that day
        stdres_xy = influence_xy.resid_studentized_internal  # Normalized residual

        model_yx = sm.OLS(xdata, sm.add_constant(ydata)).fit()
        influence_yx = model_yx.get_influence()
        residualerror_yx = influence_yx.resid.std()  # Error for that day
        stdres_yx = influence_yx.resid_studentized_internal  # Normalized residual

        if stder_xy / residualerror_xy < stder_yx / residualerror_yx:
            adfTest = adfuller(influence_xy.resid, autolag='AIC')
            beta = result_xy.slope
            intercept = result_xy.intercept
            std_residual = residualerror_xy
            latest_stdresidual = stdres_xy[-1]
            latest_residual = influence_xy.resid[-1]
        else:
            adfTest = adfuller(influence_yx.resid, autolag='AIC')
            beta = result_yx.slope
            intercept = result_yx.intercept
            std_residual = residualerror_yx
            latest_stdresidual = stdres_yx[-1]
            latest_residual = influence_yx.resid[-1]

        if adfTest[1] < 0.10 and cor > 0.88:
            stock1_name = stock1.replace(".NS", "")
            stock2_name = stock2.replace(".NS", "")
            png_file = f"{stock1_name}_{stock2_name}.png"

            stock_pair_list = os.listdir(image_directory)
            file_path = os.path.join(image_directory, png_file) if png_file in stock_pair_list else "not_available"
            file_path = file_path.replace("\\", "/")

            latest_stdresidual = latest_stdresidual.astype(float)
            stock1_price = stock1_price.astype(float)
            std_residual - std_residual.astype(float)
            latest_residual = latest_residual.astype(float)

            risk = ((4 - abs(latest_stdresidual)) / stock1_price) * std_residual * 100
            reward = abs(latest_residual / stock1_price) * 100
            RR = reward / risk

            result = OrderedDict({
                f"{stock1_name}_{stock2_name}": OrderedDict({
                    "Company2 (Y)": {f"{stock1}": round(stock1_price, 2)},
                    "Company1 (X)": {f"{stock2}": round(stock2_price, 2)},
                    "Sector": mlist[2],
                    "P-value": round(adfTest[1], 5),
                    "beta": round(beta, 4),
                    "intercept": round(intercept, 4),
                    "std_residual": round(std_residual, 3),
                    "latest_stdresidual": round(latest_stdresidual, 4),
                    "latest_residual": round(latest_residual, 3),
                    "Correlation": round(cor, 3),
                    "graph_path": file_path,
                    "MORE DETAILS": OrderedDict({
                        "Reward": round(reward, 3),
                        "Risk": round(risk, 3),
                        "RR": round(RR, 3)
                        })
                })
            })
            results.append(result)

    except Exception as e:
        print(f"Error processing {mlist}: {e}")

@app.route('/pair_data', methods=['GET'])
def get_pair_data():
    def generate():
        with ThreadPoolExecutor() as executor:
            results = []
            for mlist in mliys:
                executor.submit(StockCheck, mlist, results)
                if results:
                    # Convert the latest result to JSON and yield it
                    yield json.dumps(results[-1]) + "\n"
                    results.pop()  # Remove the last result to prevent duplicates

    return Response(generate(), content_type='application/json')

@app.route('/trades', methods=['GET'])
def get_stock_pair_data():
    def generate():
        stock_pairs_df = pd.read_csv(stock_pairs_file)
        stock_pair_list = list(zip(stock_pairs_df['Company1 (X)'], stock_pairs_df['Company2 (Y)']))
        results = []
        with ThreadPoolExecutor() as executor:
            for stock_pair in stock_pair_list:
                executor.submit(process_stock_pair, stock_pair, results)

    return Response(generate(), content_type='application/json')

def process_stock_pair(stock_pair_list, results):
    stock1_name = stock_pair_list[0].replace(".NS", "")
    stock2_name = stock_pair_list[1].replace(".NS", "")
    csv_file = f"{stock1_name}_{stock2_name}.csv"
    alt_csv_file = f"{stock2_name}_{stock1_name}.csv"

    stock_pair_data = os.listdir(data_directory)
    if csv_file in stock_pair_data:
        data_path = os.path.join(data_directory, csv_file)
    elif alt_csv_file in stock_pair_data:
        data_path = os.path.join(data_directory, alt_csv_file)
    else:
        results.append({
            f'{stock2_name}-{stock1_name}': {
                'Trading Details': 'Data Not available'
            }
        })
        return

    df = pd.read_csv(data_path)

    trades = df['Trades'][:6].tolist()
    investment = df['Investments'][:6].tolist()
    net_invest = df['Net Investments'][:6].tolist()
    trade_length = df['Trade Length'][:6].tolist()
    percentage_return = df['Percentage Return'][:6].tolist()
    profit = df['Profit'][:6].tolist()

    # Filter out NaN values if present
    trades = [val for val in trades if pd.notna(val)]
    investment = [val for val in investment if pd.notna(val)]
    net_invest = [val for val in net_invest if pd.notna(val)]
    trade_length = [val for val in trade_length if pd.notna(val)]
    percentage_return = [val for val in percentage_return if pd.notna(val)]
    profit = [val for val in profit if pd.notna(val)]

    result_dict = OrderedDict({
        trades[i]: OrderedDict({
            'Investment': investment[i],
            'Net Investment': net_invest[i],
            'Trade Length': trade_length[i],
            'Percentage Return': percentage_return[i],
            'Profit': profit[i]
        })
        for i in range(len(trades))
    })

    results.append({
        f'{stock2_name}-{stock1_name}': {
            'Trading Details': result_dict
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
