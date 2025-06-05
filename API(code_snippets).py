#if csv_file in stock_pair_data:
                #data_path = os.path.join(data_directory, csv_file)
                #df = pd.read_csv(data_path)
                #closing_price_stock1 = df[f"{stock1} Y"].iloc[-1]
                #closing_price_stock2 = df[f"{stock2} X"].iloc[-1]
                #residual = df['Residual'].iloc[-1]
                #coint = df['Coint'].iloc[-1]

                #trades = df['Trades'][:5].tolist()
                #investment = df['Investments'][:5].tolist()
                #net_invest = df['Net Investments'][:5].tolist()
                #trade_length = df['Trade Length'][:5].tolist()
                #percentage_return = df['Percentage Return'][:5].tolist()
                #profit = df['Profit'][:5].tolist()

                #trades = [val for val in trades if pd.notna(val)]
                #investment = [val for val in investment if pd.notna(val)]
                #net_invest = [val for val in net_invest if pd.notna(val)]
                #trade_length = [val for val in trade_length if pd.notna(val)]
                #percentage_return = [val for val in percentage_return if pd.notna(val)]
                #profit = [val for val in profit if pd.notna(val)]

                #result_dict = {
                #    trades[i]: {
                #        'investment': investment[i],
                #        'net investment': net_invest[i],
                #        'trade length': trade_length[i],
                #        'percentage return': percentage_return[i],
                #        'profit': profit[i]
                #  }
                #     for i in range(len(trades))
                #}

                #for pair in results:
                #    for key,value in pair.items():
                #        value[f'{stock1_name}-Closing'] = closing_price_stock1 
                #        value[f'{stock2_name}-Closing'] = closing_price_stock2 
                #        value['Cointegration'] = coint
                #        value['Residual'] = residual
                #        value['Trading Details'] = result_dict
                #        


            #else:
                #stock1_data = yf.download(stock1, period='1d')
                #stock2_data = yf.download(stock2, period='1d')

                #stock1_closing_price = stock1_data['Adj Close'].iloc[-1]
                #stock2_closing_price = stock2_data['Adj Close'].iloc[-1]

                #for pair in results:
                #    for key,value in pair.items():
                #        value['Trading details'] = "not available"  

import yfinance as yf
import datetime
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
from scipy import stats
from itertools import combinations
import threading
from flask import Flask, jsonify
import pandas as pd
import os

app = Flask(__name__)

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=2*365)

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

result_lock = threading.Lock()

def cheg_list(total_list):
    rlist = []
    for all_list in total_list:
        s1 = all_list[0]
        s2 = all_list[1]
        if os.path.exists(fr"C:\Users\pramo\Documents\GitHub\PairTrader\Data\Yt Stock Data\{s1}_{s2}_StoredData.csv"):
            df = pd.read_csv(fr"C:\Users\pramo\Documents\GitHub\PairTrader\Data\Yt Stock Data\{s1}_{s2}_StoredData.csv")
        elif os.path.exists(fr"C:\Users\pramo\Documents\GitHub\PairTrader\Data\Yt Stock Data\{s2}_{s1}_StoredData.csv"):
            df = pd.read_csv(fr"C:\Users\pramo\Documents\GitHub\PairTrader\Data\Yt Stock Data\{s2}_{s1}_StoredData.csv")
        else:
            continue
        
        cor = df[s1].corr(df[s2])
        if cor > 0.84:
            rlist.append(all_list)
    return rlist

mliys = cheg_list(total_list)

results = []

def StockCheck(mlist):
    stock1 = mlist[0]
    stock2 = mlist[1]
    
    data = pd.read_csv(fr"C:\Users\pramo\Documents\GitHub\PairTrader\Data\Yt Stock Data\{stock1}_{stock2}_StoredData.csv")
    image_directory = r'C:\\Users\\pramo\\Documents\\GitHub\\PairTrader\\Data\\Graph'
    data_directory = r'C:\\Users\\pramo\\Documents\\GitHub\\PairTrader\\Data\\FinalBacktestData'

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
        residualerror_xy = influence_xy.resid.std()  # Error for that day (lastest_residual)
        stdres_xy = influence_xy.resid_studentized_internal  # Normalized residual (latest_stdresidual)

        model_yx = sm.OLS(xdata, sm.add_constant(ydata)).fit()
        influence_yx = model_yx.get_influence()
        residualerror_yx = influence_yx.resid.std()  
        stdres_yx = influence_yx.resid_studentized_internal  

        # Determine which regression has smaller standard error ratio
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

            #risk = [(4-abs(latest_stdresidual))/stock1]*std_residual*100
            #reward = abs(latest_residual/stock1)*100
            #RR = reward/risk

            results.append({
                f"{stock1_name}_{stock2_name}": {
                    "Company2 (Y)": stock1,
                    "Company1 (X)": stock2,
                    f"{stock1}": stock1_price,
                    f"{stock2}": stock2_price,
                    "Sector": mlist[2],
                    "P-value": adfTest[1],
                    "beta": beta,
                    "intercept": intercept,
                    "std_residual": std_residual,
                    "latest_stdresidual": latest_stdresidual,  # Normalized residual
                    "latest_residual": latest_residual,  # Error for that day
                    "Correlation": cor,
                    "graph_path": file_path
                }
            })

    except Exception as e:
        print(f"Error processing {mlist}: {e}")

@app.route('/pair_data', methods=['GET'])
def get_pair_data():
    threads = []
    global results
    results = []

    for duration in mliys:
        thread = threading.Thread(target=StockCheck, args=(duration,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return jsonify(results)

@app.route('/trades', methods=['GET'])
def get_stock_pair_data():
    stock_pairs_df = pd.read_csv(stock_pairs_file)
    stock_pair_list = list(zip(stock_pairs_df['Company1 (X)'], stock_pairs_df['Company2 (Y)']))

    results = []
    threads = []

    for stock_pair in stock_pair_list:
        thread = threading.Thread(target=process_stock_pair, args=(stock_pair, results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return jsonify(results)

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
        with result_lock:
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
            f'{stock2_name}-{stock1_name}': {
                'Trading Details': result_dict
            }
        })

if __name__ == '__main__':
    app.run(debug=True)
