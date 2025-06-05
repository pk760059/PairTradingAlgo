import os
import pandas as pd
import math
pd.options.mode.chained_assignment = None 

deletion_bool = False
loop_condn1 = True
loop_condn2 = True

# arr = os.listdir("Data/BacktestData")
current_directory = os.path.dirname(os.path.abspath(__file__))#relative path to main
target_directory = os.path.join(current_directory, 'Data', 'BacktestData') #Backtest folder path
arr = os.listdir(target_directory)


def valueofi(data):
    for i in range(len(data)) :


        if math.isnan(float(data["Trades"][i])):
            return i



for j in range(len(arr)):
    # data = pd.read_csv(f"Data/BacktestData/{arr[j]}")
    file_path = os.path.join(target_directory, arr[j])
    data = pd.read_csv(file_path)

    if float(data["Signal"][len(data)-1]) == 0:
        print(arr[j])
        print("YES")

        k = len(data)-1
        while loop_condn1:
            
            if float(data["Signal"][k]) == 1.0 or float(data["Signal"][k]) == -1.0:
                print("YES")
                data["Signal"][k] = ""
                deletion_bool = True
                loop_condn1 = False

                
            k = k - 1


    if deletion_bool == True:
        
        i = valueofi(data)
                

        data["Trades"][i-1] = ""
        data["Investments"][i-1] = ""
        data["Net Investments"][i-1] = ""
        data[data.columns[10]][i-1] = ""
        data[data.columns[11]][i-1] = ""
        data["Trade Length"][i-1] = ""
        data["Percentage Return"][i-1] = ""
        profit = float(data["Profit"][i-1])
        data["Profit"][i-1] = ""
        data["Net Percentage Return"][i-1] = ""
        data["Long Profit"][i-1] = ""
        data["Short Profit"][i-1] = ""
        data["Trade Length"][i+6] = int(data["Trade Length"][i+6])-1
        data[data.columns[11]][i+6] = float(data[data.columns[11]][i+6])-profit
        data["Signal"][len(data)-1] = ""
        


    data = data.set_index("Dates")
    # data.to_csv(f"Data/FinalBacktestData/{arr[j]}")
    data.to_csv(file_path)
    loop_condn1 = True
    deletion_bool = False
    
