from Fyers_Backtest import Backtest
from datetime import datetime
from Calculate_Returns import calculate_returns as returns
from Process_data_scores import process_stock_data as calculate_scores
import os
import pandas as pd
import multiprocessing
import time
import cProfile

def process_row(row, past_check_year,past_check_month,  trading_year_start,trading_month_start, end_date, data_interval, fno_data,current_directory,csv_path):
    try:
        # profiler = cProfile.Profile()
        # profiler.enable()
        stock1 = row['Company1 (X)']
        stock2 = row['Company2 (Y)']
        sector = row['Sector']

        stock1_margin = int(fno_data[fno_data["SYMBOLS"] == stock1]['Margin'])
        stock2_margin = int(fno_data[fno_data["SYMBOLS"] == stock2]['Margin'])

        stock1_lot_size = int(fno_data[fno_data["SYMBOLS"] == stock1]['LotSize'])
        stock2_lot_size = int(fno_data[fno_data["SYMBOLS"] == stock2]['LotSize'])

        stock1 = stock1.replace(".NS", "")
        stock2 = stock2.replace(".NS", "")

        print(f"{stock1}_{stock2}_{sector}")
        print(stock1, stock1_lot_size, stock2, stock2_lot_size)

        
        intraday = Backtest(f"{stock1}.NS", f"{stock2}.NS",
                            stock1_lot_size,
                            stock2_lot_size,
                            end_date,
                            past_check_year,
                            past_check_month,
                            trading_year_start,
                            trading_month_start,
                            data_interval,
                            1,
                            1,
                            stock1_margin,
                            stock2_margin)

        intraday.collectData_Fyers()

        # Corelation Caculation
        # start_time  = time.time()
        cor = intraday.data[intraday.stock1].corr(intraday.data[intraday.stock2])
        print(f"Correlation of {stock1} & {stock2} is {cor}")
        if cor < 0.9:
            print(f"Skipping {stock1} & {stock2} because correlation is less than 0.9")
            return 0
        # print("Time taken for this pair is ", time.time()-start_time)


        sector_stats_folder = os.path.join(current_directory, 'Data', 'Stats', sector)
        os.makedirs(sector_stats_folder, exist_ok=True)
        stats_file_path = os.path.join(sector_stats_folder, f"{stock1}_{stock2}.txt")
        with open(stats_file_path, "w+") as f:
            f.write(str(intraday.checkPast()))

        sector_backtest_folder = os.path.join(current_directory, 'Data', 'BacktestData', 'Sectorwise', sector)
        os.makedirs(sector_backtest_folder, exist_ok=True)
        backtest_file_path = os.path.join(sector_backtest_folder, f"{stock1}_{stock2}.csv")
        output, profit = intraday.pairTrading()
        output.to_csv(backtest_file_path)
        returns(backtest_file_path)  # FOR PUTTING RETURNS IN THE FILE
        calculate_scores(backtest_file_path, csv_path, stock1, stock2, sector)  # for putting values in main stock pair file
        print(backtest_file_path) # FOR
        # profiler.disable()
        # profiler.dump_stats('profile_data.prof')

        return profit

    except Exception as e:
        print(f"Error processing row {row}: {e}")
        return 0

if __name__ == '__main__':
    # Inputs and initialization
    current_directory = os.path.dirname(os.path.abspath(__file__))
    end_date = datetime.now()
    data_interval = "15"#resolution
    max_processes = 1  # Set the maximum number of concurrent processes

    # Taking inputs from user if user does not give input default values are taken
    user_input = input("If you want to give inputs for time interval Enter Y: ")
    if user_input == "Y":
        past_check_year = int(input("Enter year from where to start past check please enter in format YYYY:"))
        past_check_month = int(input("Enter month from where to start past check please enter in formant MM:"))
        trading_year_start = int(input("Enter year from where to start trading interval please enter in format YYYY:"))
        trading_month_start = int(input("Enter month from where to start trading interval please enter in formant MM:"))
    else:
        #1-12 months
        past_check_year = 2024
        past_check_month = 2
        trading_year_start = 2024
        trading_month_start = 3

    total_profit = 0

    csv_path = os.path.join(current_directory, 'Input', 'FNO.csv')
    fno_data = pd.read_csv(csv_path)

    csv_path = os.path.join(current_directory, 'Output', 'stocks_pairs.csv')
    data = pd.read_csv(csv_path)

    # Prepare arguments for multiprocessing
    args = [(row, past_check_year,past_check_month, trading_year_start,trading_month_start, end_date, data_interval, fno_data,current_directory,csv_path) 
            for _, row in data.iterrows()]

    with multiprocessing.Pool(processes=max_processes) as pool:
        results = pool.starmap(process_row, args)

    total_profit = sum(results)
    print(total_profit)
