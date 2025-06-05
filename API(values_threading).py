import yfinance as yf
import datetime
import numpy
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
from scipy import stats
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify
import pandas as pd
import os
from collections import OrderedDict
from flask_cors import CORS 

#ALL THE DIRECTORIES WHICH ARE ALL GLOBAL
DATA_DIRECTORY = r"C:\\Users\\pramo\\Documents\\GitHub\\PairTrader\\Data\\Sectorwise2019"
IMAGE_DIRECTORY =  r"C:\\Users\\pramo\\Documents\\GitHub\\PairTrader\\Data\\Graph"
STOCK_PAIRS_FILE = r"C:\\Users\\pramo\\Documents\\GitHub\\PairTrader\\Output\\New_Stocks_after_threading2.csv"
FNO_LIST_FILE = r"C:\\Users\\pramo\\Documents\\GitHub\\PairTrader\\Input\\FNO_LIST.csv"
YT_STOCK_DATA = r"C:\\Users\\pramo\\Documents\\GitHub\\PairTrader\\Data\\Yt Stock Data"

NUMBER_OF_DAYS_TO_CONSIDER = 250
COINT_MAX = 0.1
COINT_ALGO_COEFF = 5
LIMITING_CORR = 0.84
NUMBER_OF_YEARS_TO_CONSIDER = 1
VALUE_OF_SD_AT_POINTS = 0.6  # POINTS ARE 2 -2, 4, -4

STOCK_PAIRS_PATH = r"C:\Users\pramo\Documents\GitHub\PairTrader\Data\Sectorwise2019\stocks_pairs1.csv"
SECTORWISE_FOLDER = r'C:\Users\pramo\Documents\GitHub\PairTrader\Data\Sectorwise2019'


def SD_Algo(sd):

    k = VALUE_OF_SD_AT_POINTS

    if (sd >= 3 and sd <= 4.5):
        score = (k - 1)*sd + (4 - 3*k)
        return round(score,3)
    
    elif (sd >= 2 and sd <= 3 ):
        score = (1 - k)*sd + (3*k -2)
        return round(score,3)
    
    elif (sd <= -3 and sd >= -4.5):
        score = (1 - k)*sd + (4 - 3*k)
        return round(score,3)
    
    elif (sd <= -2 and sd >= -3):
        score = (k - 1)*sd + (3*k - 2)
        return round(score,3)
    
    elif (sd >= 0 and sd < 2):
        score = (k/2)*sd
        return round(score,3)

    elif (sd > -2 and sd <= 0):
        score = (-k/2)*sd
        return round(score,3)
    else:
        return 0 
#SD_Algo()


def corr_algo(corr):
    
    n = LIMITING_CORR
    if corr > n:
        score = (1/(1-n))*corr - (n/(1-n))
        return round(score, 3)
    else:
        return 0    
 

def Coint_Algo(cointegration_value):
    
    x = cointegration_value

    if x > 0.1:
        return 0

    elif x < 0:
        return 0

    else:
        coint_algo_score = (numpy.exp(-COINT_ALGO_COEFF * x) - numpy.exp(-COINT_ALGO_COEFF * 0.1))/(1 - numpy.exp(-COINT_ALGO_COEFF * 0.1))
        return coint_algo_score


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=2 * 365)

data = pd.read_csv(FNO_LIST_FILE)
grouped = data.groupby('Sector')
resultList = []

for key, group in grouped:
    for b, g in combinations(group['SYMBOLS'].tolist(), 2):
        resultList.append([b, g, key])

resultList.sort()
total_list = resultList

def cheg_list(total_list):
    rlist = []
    for all_list in total_list:
        s1 = all_list[0]
        s2 = all_list[1]
        file_path_1 = os.path.join(YT_STOCK_DATA, f"{s1}_{s2}_StoredData.csv")
        file_path_2 = os.path.join(YT_STOCK_DATA, f"{s2}_{s1}_StoredData.csv")
        
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
    
    file_path_1 = os.path.join(YT_STOCK_DATA, f"{stock1}_{stock2}_StoredData.csv")
    file_path_2 = os.path.join(YT_STOCK_DATA, f"{stock2}_{stock1}_StoredData.csv")

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

            stock_pair_list = os.listdir(IMAGE_DIRECTORY)
            file_path = os.path.join(IMAGE_DIRECTORY, png_file) if png_file in stock_pair_list else "not_available"
            file_path = file_path.replace("\\", "/")

            latest_stdresidual = latest_stdresidual.astype(float)
            stock1_price = stock1_price.astype(float)
            std_residual - std_residual.astype(float)
            latest_residual = latest_residual.astype(float)
    
            risk_form = ((4 - abs(latest_stdresidual)) / stock1_price) * std_residual * 100
            if risk_form > 0:
                risk = risk_form
            else:
                risk = "-"
            
            reward = abs(latest_residual / stock1_price) * 100
            RR = reward / risk
    

            result = {
                    f"{stock1_name}(Y)": round(stock1_price, 2),
                    f"{stock2_name}(X)": round(stock2_price, 2),
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
            }
            results.append(result)

    except Exception as e:
        print(f"Error processing {mlist}: {e}")

@app.route('/pair_data', methods=['GET'])

def get_pair_data():
    results = []
    with ThreadPoolExecutor() as executor:
        executor.map(lambda x: StockCheck(x, results), mliys)

    return jsonify(results)

@app.route('/trades', methods=['GET'])

def get_stock_pair_data():
    stock_pairs_df = pd.read_csv(STOCK_PAIRS_FILE)
    stock_pair_list = list(zip(stock_pairs_df['Company1 (X)'], stock_pairs_df['Company2 (Y)'], stock_pairs_df['Sector']))
    results = []
    with ThreadPoolExecutor() as executor:
        executor.map(lambda x: process_stock_pair(x, results), stock_pair_list)

    return jsonify(results)

def process_stock_pair(stock_pair_list, results):
    stock1_name = stock_pair_list[0].replace(".NS", "")
    stock2_name = stock_pair_list[1].replace(".NS", "")
    sector = stock_pair_list[2]

    sector_folder = os.path.join(DATA_DIRECTORY, str(sector))
    pair_file_path = os.path.join(sector_folder, f'{stock1_name}_{stock2_name}_returns.csv')

    if os.path.exists(pair_file_path):
        df = pd.read_csv(pair_file_path)
        df['Dates'] = pd.to_datetime(df['Dates'], format = 'mixed', dayfirst = True)
        target_row = df[(df['Signal'] == -1) | (df['Signal'] == 1)]
        total_sum_list = []
        percentage_list = []
        dates_list = []
        BUY_SELL_list = []

        for index, row in target_row.iterrows():
            target_index = row.name
            date_range = df.iloc[max(0, target_index - NUMBER_OF_DAYS_TO_CONSIDER):target_index]
            days_count = date_range[date_range['Coint'] < COINT_MAX].shape[0]

            if target_index < 250:
                if target_index == 0:
                    days_count_score = 0
                else:
                    days_count_score = days_count/target_index
            else:
                days_count_score = days_count/NUMBER_OF_DAYS_TO_CONSIDER 

            if 'Correlation' in df.columns:
                Corr = row['Correlation']
            else:
                print("-")

            if row['Signal'] == 1:
                BUY_SELL_list.append(('BUY', 'SELL'))
            else:
                BUY_SELL_list.append(('SELL', 'BUY'))

            dates = row['Dates']
            dates_list.append(dates)

            total_sum = days_count_score + SD_Algo(row['Standard Residual']) + Coint_Algo(row['Coint']) + corr_algo(Corr)
            total_sum_list.append(total_sum)
            percentage = (total_sum/4)*100
            percentage_list.append(percentage)

        trades = df['Trades'][:7].tolist()
        investment = df['Investments'][:7].tolist()
        net_invest = df['Net Investments'][:7].tolist()
        trade_length = df['Trade Length'][:7].tolist()
        percentage_return = df['Percentage Return'][:7].tolist()
        profit = df['Profit'][:7].tolist()
        x_lot_size = df['Multiplier X'][0].tolist()
        y_lot_size = df['Multiplier Y'][0].tolist()

        # Filter out NaN values if present
        trades = [val for val in trades if pd.notna(val)]
        investment = [val for val in investment if pd.notna(val)]
        net_invest = [val for val in net_invest if pd.notna(val)]
        trade_length = [val for val in trade_length if pd.notna(val)]
        percentage_return = [val for val in percentage_return if pd.notna(val)]
        profit = [val for val in profit if pd.notna(val)]

        result_dict = OrderedDict({
            trades[i]: OrderedDict({
                'signal' : row['Signal'],
                'Date of Trade' : dates_list[i],
                'Investment': investment[i],
                'Net Investment': net_invest[i],
                'Trade Length': trade_length[i],
                'Percentage Return': percentage_return[i],
                'Profit': profit[i],
                f"x(lot size){stock1_name}" : x_lot_size,
                f"x(lot size){stock2_name}" : y_lot_size,
                'yAlgoScore' : round(total_sum_list[i], 3),
                'yPercentage' : f"{round(percentage_list[i], 3)}%",
                f"x{(stock1_name)}" : BUY_SELL_list[i][0],
                f"x{(stock2_name)}" : BUY_SELL_list[i][1]

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
