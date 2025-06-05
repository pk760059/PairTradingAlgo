import pandas as pd
import numpy
import os

COINT_ALGO_COEFF = 5
LIMITING_CORR = 0.84
NUMBER_OF_DAYS_TO_CONSIDER = 250
VALUE_OF_SD_AT_POINTS = 0.6  # POINTS ARE 2 -2, 4, -4
OUTPUT_CSV_PATH = r'C:\Users\pramo\Documents\GitHub\PairTrader\Output\processed_stock_pairs.csv'
STOCK_PAIRS_PATH = r'C:\Users\pramo\Documents\GitHub\PairTrader\Data\Sectorwise2019\PAIRS_COMBINATION_RELEVANT.csv'
SECTORWISE_PATH = r'C:\Users\pramo\Documents\GitHub\PairTrader\Data\Sectorwise2019'


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

correlation_scores = []
last_corr_list = []
cointegration_scores = []
last_coint_list = []
below_coint = []
days_coint = []
SD_scores = []
last_SD_list = []
total_score_list = []
percentage_list = []

for index, row in stock_pairs_df.iterrows():
    company1 = clean_company_name(row['Company1 (X)'])
    company2 = clean_company_name(row['Company2 (Y)'])
    sector = row['Sector']
    
    #days_coint_score = days_coint_algo(row['Number of Days Cointegrated'])
    #days_coint_scores.append(days_coint_score)

    #avg_trade_time_score = Av_trade_time_algo(row['Average Trade time'])
    #avg_trade_time_scores.append(avg_trade_time_score)

    #trade_algo_score = Trade_Algo(row['Total Past trades'], row['Positive past Trades'])
    #trade_algo_scores.append(trade_algo_score)

    sector_folder = os.path.join(SECTORWISE_PATH, str(sector))
    pair_file_path = os.path.join(sector_folder, f'{company1}_{company2}.csv')

    if os.path.exists(pair_file_path):
        df = pd.read_csv(pair_file_path)
        df['Dates'] = pd.to_datetime(df['Dates'])

        target_rows = df.iloc[-1]
        results = []
        last_250_days = df.tail(250)
        coint_below_0_1_count = (last_250_days['Coint'] < 0.1).sum()
        below_coint.append((coint_below_0_1_count)/NUMBER_OF_DAYS_TO_CONSIDER)
        days_coint.append(coint_below_0_1_count)

        results_df = pd.DataFrame(results)

        if 'Correlation' in df.columns:
            last_corr = df['Correlation'].iloc[-1]
            last_corr_list.append(last_corr)
            correlation_scores.append(corr_algo(last_corr))  
        else:
            correlation_scores.append("-")

        if 'Standard Residual' in df.columns:
            last_residual = df['Standard Residual'].iloc[-1]
            last_SD_list.append(last_residual)
            SD_scores.append(SD_Algo(last_residual))
        else:
            SD_scores.append("-")
        
        last_coint = df['Coint'].iloc[-1]
        last_coint_list.append(last_coint)
        cointegration_scores.append(Coint_Algo(last_coint))

        total_score = Coint_Algo(last_coint) + SD_Algo(last_residual) + corr_algo(last_corr) + ((coint_below_0_1_count)/NUMBER_OF_DAYS_TO_CONSIDER)
        total_score = round(total_score, 3)
        total_score_list.append(total_score)
        percentage = (total_score/4)*100
        percentage_list.append(round(percentage, 3))

    else:
        correlation_scores.append("-")
        last_corr_list.append("-")
        last_SD_list.append("-")
        days_coint.append("-")
        last_coint_list.append("-")
        cointegration_scores.append("-")
        SD_scores.append("-")
        below_coint.append("-")

stock_pairs_df['Correlation'] = last_corr_list
stock_pairs_df['Corr Score'] = correlation_scores
stock_pairs_df['Coint'] = last_coint_list
stock_pairs_df['Coint Score'] = cointegration_scores
stock_pairs_df['SD'] = last_SD_list
stock_pairs_df['SD_score'] = SD_scores
stock_pairs_df['days coint'] = days_coint
stock_pairs_df['Coint_score'] = below_coint
stock_pairs_df['AlgoScore'] = total_score_list
stock_pairs_df['Percentage'] = percentage_list

output_csv_path = OUTPUT_CSV_PATH
stock_pairs_df.to_csv(output_csv_path, index=False)

print(f"Processed file saved to: {output_csv_path}")

