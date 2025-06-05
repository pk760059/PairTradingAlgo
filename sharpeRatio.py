import pandas as pd
import os
import statistics
from datetime import datetime
import re
# Calculate Return Functions

def calculateReturns2(stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y):
    returns = (stockyprev - stocky)*loty*multiplier_y + (stockx-stockxprev)*lotx*multiplier_x
    return returns


def calculateReturns1(stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y):
    returns = (stocky - stockyprev)*loty*multiplier_y + (stockxprev-stockx)*lotx*multiplier_x
    return returns

# Read all CSV Files
# arr = os.listdir("Data/FinalBacktestData")
# arr = os.listdir("Fin_data\Fin_data\Data\FinalBacktestData")
arr = os.listdir(r"Fin_data\Fin_data\Data\BacktestData\new")
# arr = os.listdir("Fin_data\Fin_data\Data\BacktestData")

# print(arr)

def scr_retrival(cname,dlist,date_format='%d-%m-%Y'):
    
    '''
    This function retrieves the data for scores from the merged and make sure the Data integrity is intact.
    It matched dates and all
    '''
    # print(type(dlist[0]))
    
    ndate=[]
    for date_str in dlist:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d-%m-%Y")
            ndate.append(formatted_date)
        except ValueError:
            print(f"Invalid date format: {date_str}")
    dlist=ndate
    try:
        x2df=pd.read_csv(fr'C:\Users\acer\Desktop\Py-Fin\Fin_data\Fin_data\Data\Merged Scores\{cname}.csv')
        # x2df=pd.read_csv(f'Data\Merged Scores\{cname}.csv')
        # print(x2df)
        # print("ran")
        x2df['DateTime'] = pd.to_datetime(x2df['DateTime'], format=date_format)

        dlist = pd.to_datetime(dlist, format=date_format)
        
        dates_df = pd.DataFrame(dlist, columns=['DateTime'])

        # Merge the dates_df with x2df to ensure all dates from dlist are included
        filtered_df = pd.merge(dates_df, x2df, on='DateTime', how='left')
        filtered_df['DateTime'] = filtered_df['DateTime'].dt.strftime(date_format)
        # filtered_df = x2df[x2df['DateTime'].isin(dlist)]
        filtered_df=filtered_df.iloc[:,1:]
        return filtered_df

    except Exception as e:
        print(f'Issue in finding {cname} merged file,{e}')
        return None

# def f_para(search_list,txt):
#     pattern = fr'^{txt}\s'  

#     for idx,ele in enumerate(search_list):

#         if isinstance(ele, str):
#             # print('str detechted')
#             x = re.search(pattern, ele)
#             if x :
#                 print(ele,'Found at',idx)
#                 return idx


def Mega_s(df, w1, w2):
    """
    Filters a DataFrame based on two words (w1, w2) and prints the matching elements along with their row indices and column names.

    Args:
        df (pandas.DataFrame): The DataFrame to filter.
        w1 (str): The first word.
        w2 (str): The second word.
    """

    # Check for empty DataFrame
    if df.empty:
        print("Empty DataFrame provided.")
        return

    for col in df.columns:
        # Check data type before using .str methods
        if col.startswith(w1) and col.endswith(w2):
            # print(col)
            return None,col 
        
        
        if df[col].dtype == object:
            # String data, proceed with vectorized methods
            filtered_df = df[df[col].str.startswith(w1) & df[col].str.endswith(w2)]
            if not filtered_df.empty:
                for index, row in filtered_df.iterrows():
                    # print(f"Element at row {index}, column '{col}': {row[col]}")
                    return index ,col
        else:
            # Non-string data, skip or consider conversion if applicable
            pass  # Or convert to string if meaningful (df[col].astype(str))


for j in range(len(arr)):
    # Check Variables
    isTrading1 = False
    isTrading2 = False
    breakvariable = 0

    # Data Variables
    tradeNumber = 0
    risk_free_rate = 0


    #Reading CSV
    # data = pd.read_csv(f"Data/FinalBacktestData/{arr[j]}")
    # data = pd.read_csv(f"Fin_data\Fin_data\Data\FinalBacktestData\{arr[j]}")last
    data = pd.read_csv(fr"Fin_data\Fin_data\Data\BacktestData\new\{arr[j]}")
    print(f"Fin_data\Fin_data\Data\FinalBacktestData\{arr[j]}")
    # print("Data-->",data.info())
    # print(data[data.columns[21]])

# Getting Lot Sizes, and Margin

    for i in range(len(data)):
        if data[data.columns[7]][i] == "Individual Breakup":
            breakvariable = i+1
            break

    # sy_list= data['Net Investments']
    # sx_list= data['Net Investments']
    
    r1,c1=Mega_s(data.copy(), 'Margin', 'X')
    r2,c2=Mega_s(data.copy(), 'Margin', 'Y')
    r3,c3=Mega_s(data.copy(), 'Lot', 'Y')
    r4,c4=Mega_s(data.copy(), 'Lot', 'X')
    
    marginx = float(data[c1][r1+1])
    marginy = float(data[c2][r2+1])
    loty = float(data[c3][r3+1])
    lotx = float(data[c4][r4+1])

    # Calculating Sharpe Ratio

    ParentReturnsList = []
    # ParentPercentageReturnsList = []
    returnsList = []
    percentage_returns_list = []
    # std_deviation_list = []
    # mean_list = []
    # sharpe_ratio_list = []
    # sortino_ratio_list = [] # returns-riskfreerate/negative standard deviation
    calmar_ratio_list = [] # returns-riskfreerate/max_drawdown
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
                
                r7,c7=Mega_s(data.copy(), 'Multiplier', 'X')
                r8,c8=Mega_s(data.copy(), 'Multiplier', 'Y')
                multiplier_x = float(data[c7][tradeNumber])
                multiplier_y = float(data[c8][tradeNumber])
                
                # print("here is the culprit",multiplier_x)
                # print('Values going in are', stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y)
                returns = calculateReturns2(stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y)
                percentage_returns = returns/float((data[data.columns[9]][tradeNumber]))

                # print("Return added -->",returns)
                # Appending Data to Local List
                returnsList.append(returns)
                percentage_returns_list.append(percentage_returns)

                #Appending Data to Parent List
                ParentReturnsList.append(returns)
                # ParentPercentageReturnsList.append(percentage_returns)

            elif isTrading1:

                
                stocky = float(data[data.columns[1]][i])
                stockx = float(data[data.columns[2]][i])
                
                r5,c5=Mega_s(data.copy(), 'Multiplier', 'X')
                r6,c6=Mega_s(data.copy(), 'Multiplier', 'Y')
                multiplier_x = float(data[c5][tradeNumber])
                multiplier_y = float(data[c6][tradeNumber])
                
                # print("here is the culprit",multiplier_x)
                # print('Values going in are', stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y)
                returns = calculateReturns1(stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y)
                percentage_returns = returns/float((data[data.columns[9]][tradeNumber]))
                # print("Return added -->",returns)
                
                # Appending Data to Local List
                returnsList.append(returns)
                percentage_returns_list.append(percentage_returns)

                #Appending Data to Parent List
                ParentReturnsList.append(returns)
                # ParentPercentageReturnsList.append(percentage_returns)


            std_dev = statistics.stdev(percentage_returns_list[1:])
            res = [ele for ele in percentage_returns_list if ele < 0]

            if len(res)>1:
                negative_std_dev = statistics.stdev(res)
            else:
                negative_std_dev = 0
            mean = statistics.mean(percentage_returns_list[1:])
            sharpe_ratio = (mean-risk_free_rate)/std_dev

            if negative_std_dev != 0:
                sortino_ratio = (mean-risk_free_rate)/negative_std_dev
            else:
                sortino_ratio = 0
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
            # ac_trnum=tradeNumber-1
            
                            
            r9,c9=Mega_s(data.copy(), 'Multiplier', 'X')
            r10,c10=Mega_s(data.copy(), 'Multiplier', 'Y')
            multiplier_x = float(data[c9][tradeNumber])
            multiplier_y = float(data[c10][tradeNumber])
            
            # multiplier_x = float(data['Multiplier X'][tradeNumber])
            # multiplier_y = float(data['Multiplier Y'][tradeNumber])
            # print("here is the culprit",multiplier_x)
            # print('Values going in are', stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y)
            returns = calculateReturns2(stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y)
            percentage_returns = returns/float((data[data.columns[9]][tradeNumber]))

            # print("Return added -->",returns)
            # Appending Data to Local List
            returnsList.append(returns)
            percentage_returns_list.append(percentage_returns)

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
                
            r11,c11=Mega_s(data.copy(), 'Multiplier', 'X')
            r12,c12=Mega_s(data.copy(), 'Multiplier', 'Y')
            multiplier_x = float(data[c11][tradeNumber])
            multiplier_y = float(data[c12][tradeNumber])
            
            # multiplier_x = float(data['Multiplier X'][tradeNumber])
            # multiplier_y = float(data['Multiplier Y'][tradeNumber])
            # print("here is the culprit",multiplier_x)
            # print('Values going in are', stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y)
            returns = calculateReturns1(stockyprev,stockxprev,stocky,stockx,lotx,loty,multiplier_x,multiplier_y)
            percentage_returns = returns/float((data[data.columns[9]][tradeNumber]))
            
            
            # Appending Data to Local List
            returnsList.append(returns)
            percentage_returns_list.append(percentage_returns)
            # print("Return added -->",returns)
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
    # print("Parent return list-->",ParentReturnsList)
    # df1["Percentage Returns"] = ParentPercentageReturnsList
    # df1["Standard Deviation"] = std_deviation_list#
    # df1["Mean"] = mean_list#
    # df1["Sharpe Ratio"] = sharpe_ratio_list#
    # df1["Sortino Ratio"] = sortino_ratio_list#



    df2 = data

    date_list=data['Dates']
    fin_scr=pd.DataFrame()
    
    y=data.columns[1] # ye Y ka h 
    y=y[:-5]
    
    x=data.columns[2] # ye X ka h 
    x=x[:-5]
    print(x,y)
    scrdfc1=scr_retrival(y,date_list)
    scrdfc2=scr_retrival(x,date_list)
    
    fin_scr=pd.concat([scrdfc1.iloc[:,:1],scrdfc2.iloc[:,:1],scrdfc1.iloc[:,1:],scrdfc2.iloc[:,1:]],axis=1)
    # print("Fin_scr ------>",fin_scr)
    output = pd.concat([df2,df1],axis=1)
    print(df1.info())
    print(df2.info())
    output = output[[data.columns[0],
    data.columns[1],
    data.columns[2],
    data.columns[3],
    data.columns[4],
    data.columns[5],
    data.columns[6],
    "Returns",
    # "Percentage Returns",
    # "Standard Deviation",
    # "Mean",
    # "Sharpe Ratio",
    # "Sortino Ratio",
    data.columns[7],
    data.columns[12],
    data.columns[8],
    data.columns[9],
    data.columns[10],
    data.columns[11],
    data.columns[13],
    data.columns[15],
    data.columns[16],
    data.columns[17],
    data.columns[14]]]
    
    # print(output)
    
    # foutput=pd.concat([output],axis=1)
    # co_order=[0,1,2,3,4,5,6,7,19,20,21,22,8,9,10,11,12,13,14,15,16,17,18]
    # ndf=foutput[foutput.columns[co_order]]
    # ndf.to_csv(fr"Fin_data\Fin_data\Data\SharpeRatio\new\{arr[j]}")
    output.to_csv(fr"Fin_data\Fin_data\Data\SharpeRatio\new\{arr[j]}")