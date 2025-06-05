import pandas as pd
import numpy 
import os 

#GLOBAL VARIABLES
NUMBER_OF_DAYS_TO_CONSIDER = 250
COINT_MAX = 0.1
COINT_ALGO_COEFF = 5
LIMITING_CORR = 0.84
NUMBER_OF_YEARS_TO_CONSIDER = 1
VALUE_OF_SD_AT_POINTS = 0.6  # POINTS ARE 2 -2, 4, -4

def Trade_Algo(total_trades, positive_trades):

    if total_trades < 5:
        return round(positive_trades / total_trades, 3) if total_trades != 0 else 0
    else:
        trade_algo_score = (positive_trades + 1)/total_trades
        if trade_algo_score > 1:
            trade_algo_score = 1
        return round(trade_algo_score, 3)

#Trade_Algo()


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

#corr_algo()

def days_coint_algo(days):
    
    total_days = 250

    score = days/total_days
    return round(score, 4)


#days_coint_algo()

def Av_trade_time_algo(av_time):
    if av_time >= 1 and av_time < 5:
        return 1
    elif av_time >= 5 and av_time < 10:
        return 0.8
    elif av_time >= 10 and av_time < 15:
        return 0.7
    elif av_time >= 15 and av_time < 20:
        return 0.6
    elif av_time >= 20 and av_time < 25:
        return 0.5
    elif av_time >= 25 and av_time < 30:
        return 0.4
    elif av_time >= 30 and av_time < 35:
        return 0.2
    else:
        return 0  
  
#Av_trade_time_algo()  

def Coint_Algo(cointegration_value):
    
    x = cointegration_value

    if x > 0.1:
        return 0

    elif x < 0:
        return 0

    else:
        coint_algo_score = (numpy.exp(-COINT_ALGO_COEFF * x) - numpy.exp(-COINT_ALGO_COEFF * 0.1))/(1 - numpy.exp(-COINT_ALGO_COEFF * 0.1))
        return coint_algo_score


stock_pairs_path = r'C:\Users\pramo\Documents\GitHub\PairTrader\Output\stocks_pairs.csv'
sectorwise_path = r'C:\Users\pramo\Documents\GitHub\PairTrader\Data\Sectorwise2019'


stock_pairs_df = pd.read_csv(stock_pairs_path)

def clean_company_name(name):
    if isinstance(name, str):
        return name.replace('.NS', '')
    else:
        return 'Unknown'  
    
days_coint_scores = []
avg_trade_time_scores = []
trade_algo_scores = []
correlation_scores = []
cointegration_scores = []
below_coint = []
SD_scores = []
    
for index, row in stock_pairs_df.iterrows():
    company1 = clean_company_name(row['Company1 (X)'])
    company2 = clean_company_name(row['Company2 (Y)'])
    sector = row['Sector']

    sector_folder = os.path.join(sectorwise_path, str(sector))
    pair_file_path = os.path.join(sector_folder, f'{company1}_{company2}.csv')



