import pandas as pd
import os
import math
import calendar
from datetime import datetime
from dateutil import parser
import statistics

arr = os.listdir("Data/SharpeRatio")

TotalOverallProfit = 0
AverageTradeTime = 0
AverageTradeCost = 0
TotalOverallTrades = 0
overall_monthly_returns = {
    "Jan":0,
    "Feb":0,
    "Mar":0,
    "Apr":0,
    "May":0,
    "Jun":0,
    "Jul":0,
    "Aug":0,
    "Sep":0,
    "Oct":0,
    "Nov":0,
    "Dec":0
}
print(overall_monthly_returns)


macro_trade_output = {
    'Stock_Name':[],
    'Total Profit':[],
    'Average Trade Cost':[],
    'Average Trade Time':[],
    'Total Trades':[],
    'Sharpe Ratio':[]
}

monthly_returns_output = {
    'Stock_Name':[],
    'Jan':[],
    'Feb':[],
    'Mar':[],
    'Apr':[],
    'May':[],
    'Jun':[],
    'Jul':[],
    'Aug':[],
    'Sep':[],
    'Oct':[],
    'Nov':[],
    'Dec':[]
}

df = pd.DataFrame(macro_trade_output)
df2 = pd.DataFrame(monthly_returns_output)

risk_free_rate = 0

for j in range(len(arr)):
    stock_name = arr[j].replace(".csv","")
    print(stock_name)

    percentage_returns_list = []

    monthly_returns = {
    "Jan":0,
    "Feb":0,
    "Mar":0,
    "Apr":0,
    "May":0,
    "Jun":0,
    "Jul":0,
    "Aug":0,
    "Sep":0,
    "Oct":0,
    "Nov":0,
    "Dec":0
}

    data = pd.read_csv(f"Data/SharpeRatio/{arr[j]}")
    data_filtered = data.fillna(0)

    total_profit = 0
    total_trade_time = 0
    total_trade_cost = 0
    total_trades = 0

    # Total Profits and Trade
    for i in range(len(data)):


        if math.isnan(float(data["Trades"][i])):

            break

        total_trade_cost += float(data_filtered["Net Investments"][total_trades])
        total_trade_time += float(data_filtered["Trade Length"][total_trades])

        total_profit += float(data_filtered["Profit"][total_trades])

        total_trades += 1

    if total_trades != 0:
        print(f"Total Profit : {total_profit}")
        print(f"Average Trade Cost: {total_trade_cost/total_trades}")
        print(f"Average Trade Time : {total_trade_time/total_trades}")
        print(f"Total Trades: {total_trades}")
        print("\n")
        print("\n")

    else:
        total_profit = 0
        total_trade_cost = 0
        print(f"Total Profit : {total_profit}")
        print(f"Average Trade Cost: 0")
        print(f"Average Trade Time : 0")
        print(f"Total Trades: 0")
        print("\n")
        print("\n")




    TotalOverallProfit += total_profit
    TotalOverallTrades += total_trades
    if total_trades == 0:
        AverageTradeCost = 0
        AverageTradeTime = 0
    else:
        AverageTradeCost += total_trade_cost/total_trades
        AverageTradeTime += total_trade_time/total_trades



    # Monthly Returns
    for i in range(len(data)):

        if data["Signal"][i] == 0:
            profit = data["Returns"][i]

            month = parser.parse((str(data["Dates"][i]))).month
            temp_profit = monthly_returns[calendar.month_abbr[month]]
            overall_temp_profit = overall_monthly_returns[calendar.month_abbr[month]]
            profit = temp_profit+profit
            overallprofit = overall_temp_profit+profit
            monthly_returns[calendar.month_abbr[month]] = profit
            overall_monthly_returns[calendar.month_abbr[month]] = overallprofit

    df2.loc[len(df2.index)] = [stock_name,
    monthly_returns[calendar.month_abbr[1]],
    monthly_returns[calendar.month_abbr[2]],
    monthly_returns[calendar.month_abbr[3]],
    monthly_returns[calendar.month_abbr[4]],
    monthly_returns[calendar.month_abbr[5]],
    monthly_returns[calendar.month_abbr[6]],
    monthly_returns[calendar.month_abbr[7]],
    monthly_returns[calendar.month_abbr[8]],
    monthly_returns[calendar.month_abbr[9]],
    monthly_returns[calendar.month_abbr[10]],
    monthly_returns[calendar.month_abbr[11]],
    monthly_returns[calendar.month_abbr[12]]
    ]


    for i in range(len(data)):
        if data_filtered["Percentage Returns"][i] == 0:
            pass
        else:
            percentage_returns_list.append(float(data_filtered["Percentage Returns"][i]))
    
    if len(percentage_returns_list)>= 2:
        std_dev = statistics.stdev(percentage_returns_list)
        mean = statistics.mean(percentage_returns_list)
        sharpe_ratio = (mean-risk_free_rate)/std_dev
    else:
        std_dev = 0
        mean = 0
        sharpe_ratio = 0

    if total_trades != 0:
        df.loc[len(df.index)] = [stock_name,total_profit,total_trade_cost/total_trades,total_trade_time/total_trades,total_trades,sharpe_ratio]
    else:
        df.loc[len(df.index)] = [stock_name,total_profit,0,0,total_trades,sharpe_ratio]




print(f"Total Overall Profit: {TotalOverallProfit}")
print(f"Total Overall Trades: {TotalOverallTrades}")
print(f"Average Trade Time: {AverageTradeTime/len(arr)}")
print(f"Average Trade Cost: {AverageTradeCost/len(arr)}")


# df = pd.DataFrame()
# df["Total Profit"] = [TotalOverallProfit]
# df["Total Trades"] = [TotalOverallTrades]
# df["Average Trade Time"] = [AverageTradeTime/len(arr)]
# df["Average Trade Cost"] = [AverageTradeCost/len(arr)]


df2.loc[len(df2.index)] = ["Overall",
    overall_monthly_returns[calendar.month_abbr[1]],
    overall_monthly_returns[calendar.month_abbr[2]],
    overall_monthly_returns[calendar.month_abbr[3]],
    overall_monthly_returns[calendar.month_abbr[4]],
    overall_monthly_returns[calendar.month_abbr[5]],
    overall_monthly_returns[calendar.month_abbr[6]],
    overall_monthly_returns[calendar.month_abbr[7]],
    overall_monthly_returns[calendar.month_abbr[8]],
    overall_monthly_returns[calendar.month_abbr[9]],
    overall_monthly_returns[calendar.month_abbr[10]],
    overall_monthly_returns[calendar.month_abbr[11]],
    overall_monthly_returns[calendar.month_abbr[12]]
    ]

df.to_csv("Output/Marco.csv")

df2.to_csv("Output/MonthlyReturns.csv")

print(overall_monthly_returns)