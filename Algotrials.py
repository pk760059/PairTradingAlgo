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

STOCK_PAIRS_PATH = r"C:\Users\pramo\Documents\GitHub\PairTrader\Data\Sectorwise2019\stocks_pairs1.csv"
SECTORWISE_FOLDER = r'C:\Users\pramo\Documents\GitHub\PairTrader\Data\Sectorwise2019'
OUTPUT_PATH = r'C:\Users\pramo\Documents\GitHub\PairTrader\Output\results.csv'

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

stock_pairs_df = pd.read_csv(STOCK_PAIRS_PATH)

def clean_company_name(name):
    if isinstance(name, str):
        return name.replace('.NS', '')
    else:
        return 'Unknown'  
    
for index, row in stock_pairs_df.iterrows():
    company1 = clean_company_name(row['Company1 (X)'])
    company2 = clean_company_name(row['Company2 (Y)'])
    sector = row['Sector']

    sector_folder = os.path.join(SECTORWISE_FOLDER, str(sector))
    pair_file_path = os.path.join(sector_folder, f'{company1}_{company2}_returns.csv')


    if os.path.exists(pair_file_path):
        df = pd.read_csv(pair_file_path)
        df['Dates'] = pd.to_datetime(df['Dates'], format = 'mixed', dayfirst = True)
        target_rows = df[(df['Signal'] == -1) | (df['Signal'] == 1)]
        results = []

        for index, row in target_rows.iterrows():
            target_index = row.name
            #if target_index < 250:
            #    x = target_index
            #else:
            #    x = NUMBER_OF_DAYS_TO_CONSIDER

            date_range = df.iloc[max(0, target_index - NUMBER_OF_DAYS_TO_CONSIDER):target_index]
            days_count = date_range[date_range['Coint'] < COINT_MAX].shape[0]
            what_to_do = []

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
            
            total_sum = days_count_score + SD_Algo(row['Standard Residual']) + Coint_Algo(row['Coint']) + corr_algo(Corr)
            percentage = (total_sum/4)*100
            pair_file_path_df = pd.read_csv(pair_file_path)

            results.append({'target_date': row['Dates'], 
                #'signal': row['Signal'],
                'sector': sector,
                f'{company1}_{company2}': days_count,
                'cointday_sc': round(days_count_score, 3),
                'SD': round(row['Standard Residual'], 3),
                'SD_sc' : round(SD_Algo(row['Standard Residual']), 3),
                'Coint': round(row['Coint'], 3),
                'Coint_sc' : round(Coint_Algo(row['Coint']), 3),
                'corr': round(Corr, 3),
                'corr_sc' : round(corr_algo(Corr), 3),
                'total' : f"{total_sum}",
                '%': f"{percentage}"
            })

results_df = pd.DataFrame(results)
results_df.to_csv(OUTPUT_PATH, index=False)
print(f"Results saved to {OUTPUT_PATH}")
        


