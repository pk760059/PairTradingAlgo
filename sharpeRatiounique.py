import pandas as pd
import os
import statistics
import numpy as np

pd.options.mode.chained_assignment = None
import shutil


def clear_or_create_directory(path):
    # Check if the directory exists
    if os.path.exists(path):
        # Clear the directory by removing it and then recreating it
        shutil.rmtree(path)
        os.makedirs(path)
    else:
        # If the directory does not exist, create it
        os.makedirs(path)


def calculate_minima(df):
    minima_list = []
    current_list = []
    processing_segment = False  # Indicates whether we are currently processing a segment

    for value in df['Returns']:
        if pd.isna(value) or value == '':
            if processing_segment:
                # If we were processing a segment and encounter NaN, calculate minima and reset
                minima_list.append(min(current_list))
                current_list = []  # Reset the list for the next segment
                processing_segment = False
        else:
            current_list.append(float(value))
            processing_segment = True  # We are now processing a segment

    if current_list:  # To handle the last segment if it doesn't end with NaN
        minima_list.append(min(current_list))

    return minima_list


# Now call the function and pass your DataFrame


def calculateReturns2(stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y):
    returns = (stockyprev - stocky)*loty*multiplier_y + (stockx-stockxprev)*lotx*multiplier_x
    return returns


def calculateReturns1(stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y):
    returns = (stocky - stockyprev)*loty*multiplier_y + (stockxprev-stockx)*lotx*multiplier_x
    return returns


def sharpe_ratio_calculator(year):

    data_path = f"Data/BacktestData/{year}"
    output_path = f"Data/SharpeRatio/{year}"
    arr = os.listdir(data_path)

    print(arr)


    for j in range(len(arr)):
        # Check Variables
        isTrading1 = False
        isTrading2 = False
        breakvariable = 0

        # Data Variables
        tradeNumber = 0
        risk_free_rate = 0


        #Reading CSV
        data = pd.read_csv(f"{data_path}/{arr[j]}")

    # Getting Lot Sizes, and Margin

        for i in range(len(data)):
            if data[data.columns[8]][i] == "Individual Breakup":
                breakvariable = i+1
                break

        marginx = float(data[data.columns[8]][breakvariable+1])
        marginy = float(data[data.columns[9]][breakvariable+1])
        loty = float(data[data.columns[10]][breakvariable])
        lotx = float(data[data.columns[11]][breakvariable])

        # Calculating Sharpe Ratio

        ParentReturnsList = []
        # ParentPercentageReturnsList = []
        returnsList = []
        # percentage_returns_list = []
        # std_deviation_list = []
        # mean_list = []
        # sharpe_ratio_list = []
        # sortino_ratio_list = [] # returns-riskfreerate/negative standard deviation
        # calmar_ratio_list = [] # returns-riskfreerate/max_drawdown
        # Average Anual Rate of Return/ max_drawdown
        # Max_drawdown 
        stockyprev = 0
        stockxprev = 0



        for i in range(len(data)):
            # print(i)


            #Exit Trade
            if(float(data[data.columns[6]][i]) == 0):
                if isTrading2:

                    stocky = float(data[data.columns[1]][i])
                    stockx = float(data[data.columns[2]][i])
                    multiplier_x = float(data[data.columns[21]][tradeNumber])
                    multiplier_y = float(data[data.columns[22]][tradeNumber])
                    returns = calculateReturns2(stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y)
                    # percentage_returns = returns/float((data[data.columns[10]][tradeNumber]))


                    # Appending Data to Local List
                    returnsList.append(returns)
                    # percentage_returns_list.append(percentage_returns)

                    #Appending Data to Parent List
                    ParentReturnsList.append(returns)
                    # ParentPercentageReturnsList.append(percentage_returns)

                elif isTrading1:

                    stocky = float(data[data.columns[1]][i])
                    stockx = float(data[data.columns[2]][i])

                    multiplier_x = float(data[data.columns[21]][tradeNumber])
                    multiplier_y = float(data[data.columns[22]][tradeNumber])
                    returns = calculateReturns1(stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y)
                    # percentage_returns = returns/float((data[data.columns[10]][tradeNumber]))
                    
                    
                    # Appending Data to Local List
                    returnsList.append(returns)
                    # percentage_returns_list.append(percentage_returns)

                    #Appending Data to Parent List
                    ParentReturnsList.append(returns)
                    # ParentPercentageReturnsList.append(percentage_returns)


                # std_dev = statistics.stdev(percentage_returns_list[1:])
                # res = [ele for ele in percentage_returns_list if ele < 0]

                # if len(res)>1:
                #     negative_std_dev = statistics.stdev(res)
                # else:
                #     negative_std_dev = 0
                # mean = statistics.mean(percentage_returns_list[1:])
                # sharpe_ratio = (mean-risk_free_rate)/std_dev

                # if negative_std_dev != 0:
                #     sortino_ratio = (mean-risk_free_rate)/negative_std_dev
                # else:
                #     sortino_ratio = 0
                isTrading1 = False
                isTrading2 = False
                stockyprev = 0
                stockxprev = 0

                # Appending Data
                percentage_returns_list = []
                returnsList = []

                # std_deviation_list.append(std_dev)
                # mean_list.append(mean)
                # sharpe_ratio_list.append(sharpe_ratio)
                # sortino_ratio_list.append(sortino_ratio)
                tradeNumber += 1
                continue


            elif(float(data[data.columns[6]][i]) == 1):
                print("Trading 2 Started")
                stockyprev = float(data[data.columns[1]][i])
                stockxprev = float(data[data.columns[2]][i])
                isTrading2 = True
                # Appending Data


            
            elif(float(data[data.columns[6]][i]) == -1):
                print("Trading 1 Started")
                stockyprev = float(data[data.columns[1]][i])
                stockxprev = float(data[data.columns[2]][i])
                isTrading1 = True

                # Appending Data



            if(isTrading2):

                stocky = float(data[data.columns[1]][i])
                stockx = float(data[data.columns[2]][i])

                multiplier_x = float(data[data.columns[21]][tradeNumber])
                multiplier_y = float(data[data.columns[22]][tradeNumber])
                returns = calculateReturns2(stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y)
                # percentage_returns = returns/float((data[data.columns[10]][tradeNumber]))


                # Appending Data to Local List
                returnsList.append(returns)
                # percentage_returns_list.append(percentage_returns)

                #Appending Data to Parent List
                ParentReturnsList.append(returns)
                # ParentPercentageReturnsList.append(percentage_returns)
                # std_deviation_list.append("")
                # mean_list.append("")
                # sharpe_ratio_list.append("")
                # sortino_ratio_list.append("")


            elif(isTrading1):

                stocky = float(data[data.columns[1]][i])
                stockx = float(data[data.columns[2]][i])

                multiplier_x = float(data[data.columns[21]][tradeNumber])
                multiplier_y = float(data[data.columns[22]][tradeNumber])
                returns = calculateReturns1(stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y)
                # percentage_returns = returns/float((data[data.columns[10]][tradeNumber]))
                
                
                # Appending Data to Local List
                returnsList.append(returns)
                # percentage_returns_list.append(percentage_returns)

                #Appending Data to Parent List
                ParentReturnsList.append(returns)
                # ParentPercentageReturnsList.append(percentage_returns)
                # std_deviation_list.append("")
                # mean_list.append("")
                # sharpe_ratio_list.append("")
                # sortino_ratio_list.append("")

            else:
                ParentReturnsList.append("")
                # ParentPercentageReturnsList.append("")
                # std_deviation_list.append("")
                # mean_list.append("")
                # sharpe_ratio_list.append("")
                # sortino_ratio_list.append("")

        df1 = pd.DataFrame()
        df1["Returns"] = ParentReturnsList
        # df1["Percentage Returns"] = ParentPercentageReturnsList
        # df1["Standard Deviation"] = std_deviation_list
        # df1["Mean"] = mean_list
        # df1["Sharpe Ratio"] = sharpe_ratio_list
        # df1["Sortino Ratio"] = sortino_ratio_list
        minima_list = calculate_minima(df1)
        Max_Investment_list = []


        df2 = data
        investment_values = []

# Iterate through each value in the 'Net Investments' column
        for value in df2['Net Investments']:
            if pd.isna(value):
                # Break the loop if a NaN value is encountered
                break
            else:
                # Append the value to the list if it's not NaN
                investment_values.append(value)
        #investment_values = df2['Net Investments'].tolist()
        # Convert the investment column to a list
        investment_values = [float(investment) if isinstance(
            investment, str) else investment for investment in investment_values]

        adjusted_values = [investment - minima for investment, minima in zip(investment_values, minima_list)]



        output = pd.concat([df2,df1],axis=1)

        output = output[[data.columns[0],
        data.columns[1],
        data.columns[2],
        data.columns[3],
        data.columns[4],
        data.columns[5],
        data.columns[6],
        data.columns[7],
        "Returns",
        # "Percentage Returns",
        # "Standard Deviation",
        # "Mean",
        # "Sharpe Ratio",
        # "Sortino Ratio",
        data.columns[8],
        data.columns[13],
        data.columns[9],
        data.columns[10],
        data.columns[11],
        data.columns[12],
        data.columns[14],
        data.columns[16],
        data.columns[17],
        data.columns[18],
        data.columns[15]]]
        adjusted_length = len(output)
        current_adjusted_length = len(adjusted_values)

# If adjusted_values is shorter, extend it with NaNs
        if current_adjusted_length < adjusted_length:
            adjusted_values.extend([np.nan] * (adjusted_length - current_adjusted_length))
        output["Max Investment"] = adjusted_values
        output.to_csv(f"{output_path}/{arr[j]}")


for year in range(2020, 2024):

     # Clear or create directories for stats, graphs, and backtest data
     clear_or_create_directory(f"Data/SharpeRatio/{year}")
     sharpe_ratio_calculator(str(year))


