#Importing
import os
import pandas as pd
import yfinance as yf
import numpy as np
import datetime
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
from scipy import stats
from datetime import timedelta,date
import matplotlib.pyplot as plt
from LinearRegression import LinearRegression
from EntryExit import Entry1,Entry2,Exit1,Exit2

pd.options.mode.chained_assignment = None

# Backtest class
class Backtest:

    # Constructor Calling
    def __init__(self,
    stock1,
    stock2,
    lot_size_stock1,
    lot_size_stock2,
    end_date,
    time_interval,
    past_check_interval,
    trading_interval,
    data_interval,
    capital,
    comission,
    margin1,
    margin2):


        self.stock1 = stock1
        self.stock2 = stock2
        self.lot_size_stock1 = lot_size_stock1
        self.lot_size_stock2 = lot_size_stock2
        self.end_date = end_date
        self.data_interval = data_interval
        self.time_interval = time_interval
        self.past_check_interval = past_check_interval
        self.trading_interval = trading_interval

        self.capital = capital
        self.comission = comission
        self.margin1 = margin1
        self.margin2 = margin2

    def collectData(self):
        start_date = self.end_date - timedelta(days=self.time_interval*365)
        self.data = yf.download([self.stock1,self.stock2],start=start_date,end= self.end_date,interval=self.data_interval)
        self.data.fillna(method = 'ffill', inplace= True)
        self.data.fillna(method = 'bfill', inplace= True)
        self.data = self.data["Close"]
        self.data_length = int(len(self.data.index)/self.time_interval)
        self.total_data_length = int(len(self.data.index))
        print(self.data)



    def checkPast(self):
        df = pd.DataFrame()
    
        stockx,stocky,stdresidual,residual,ypred,condn,model,coint = LinearRegression(self.data[0:self.past_check_interval*self.data_length],self.stock1,self.stock2,False,True)
        self.condn = condn
        self.stockx = stockx
        self.stocky = stocky
        df[f"{stocky} Y"] = self.data[stocky][0:self.past_check_interval*self.data_length]
        df[f"{stockx} X"] = self.data[stockx][0:self.past_check_interval*self.data_length]
        df["StdResidual"] = stdresidual
        df["Residual"] = residual
        df["ypred"] = ypred
        df["Coint"] = coint
        if stockx == self.stock1:
            self.lot_size_x = self.lot_size_stock1
            self.lot_size_y = self.lot_size_stock2
            self.marginx = self.margin1
            self.marginy = self.margin2
        else:
            self.lot_size_y = self.lot_size_stock1
            self.lot_size_x = self.lot_size_stock2
            self.marginx = self.margin2
            self.marginy = self.margin1
        
        return (model.summary())


    def pairTrading(self):

        self.multiplier_x = 1
        self.multiplier_y = 1

        #Lists :
        date_list = []
        corr_list = []


        #Stock Closing Values
        stockx_closing_value_list = []
        stocky_closing_value_list = []

        #Residual and Standard Residuals
        stdresidual_list = []
        residual_list = []

        # Predicted Y
        ypred_list = []
        coint_list = []

        #Signals
        signal_list = []


        # Entry Condition List
        trade_list = []
        investment_list = []
        multiplier_list_x = []
        multiplier_list_y = []
        net_investment_list =[]
        effective_margin_list_x = []
        effective_margin_list_y = []

        effective_investment_x_list = []
        effective_investment_y_list = []

        # Exit Condition List
        trade_length_list = []
        profit_long_list = []
        profit_short_list = []
        profit_list = []
        percentage_return_list = []
        net_percentage_return_list = []

        # Parameter of Trade
        total_profit = 0
        trade_count = 0
        lot_x = self.lot_size_x
        lot_y = self.lot_size_y
        margin_x = self.marginx
        margin_y = self.marginy

        # Checks Variable
        trade_start_date = None
        trade_end_date = None
        isTradingCondn1 = False
        isTradingCondn2 = False
        stoplossTrigger1 = False
        stoplossTrigger2 = False
        trading_interval = self.past_check_interval*self.data_length


        for i in range(self.data_length*self.trading_interval):
            
            stockx,stocky,stdresidual,residual,ypred,coint = LinearRegression(self.data[i:trading_interval+i],self.stock1,self.stock2,True,self.condn)

            corr_data = self.data[i:trading_interval+i]
            cor = corr_data[self.stock1].corr(corr_data[self.stock2])
            corr_list.append(cor)

            stockx_closing_value = self.data[stockx][trading_interval+i-1]
            stocky_closing_value = self.data[stocky][trading_interval+i-1]
            stockx_closing_value_list.append(stockx_closing_value)
            stocky_closing_value_list.append(stocky_closing_value)
            stdresidual_list.append(stdresidual[-1])
            residual_list.append(residual[-1])
            ypred_list.append(ypred[-1])
            coint_list.append(coint)
            date_list.append(self.data.index[trading_interval+i-1])

            if i == self.trading_interval*self.data_length-1:
                if isTradingCondn1:
                    profit,long_profit,short_profit,percentage_return,net_percentage_return = Exit1(stockx_closing_value,
                    stocky_closing_value,
                    lot_x,
                    lot_y,
                    margin_x,
                    margin_y,
                    self.long,
                    self.short,self.multiplier_x,
                    self.multiplier_y)

                    self.multiplier_x = 1
                    self.multiplier_y = 1

                    isTradingCondn1 = False

                    trade_end_date = self.data.index[trading_interval+i-1]
                    trade_length_list.append(np.busday_count(trade_start_date.date(),trade_end_date.date()))

                    total_profit += profit
                    signal_list.append(0)

                    profit_list.append(profit)
                    profit_long_list.append(long_profit)
                    profit_short_list.append(short_profit)
                    percentage_return_list.append(percentage_return)
                    net_percentage_return_list.append(net_percentage_return)

                    #Change Check Variables Value
                    isTradingCondn1 = False
                    break


                elif isTradingCondn2:
                    profit,long_profit,short_profit,percentage_return,net_percentage_return = Exit2(stockx_closing_value,
                    stocky_closing_value,
                    lot_x,
                    lot_y,
                    margin_x,
                    margin_y,
                    self.long,
                    self.short,self.multiplier_x,
                    self.multiplier_y)

                    self.multiplier_x = 1
                    self.multiplier_y = 1

                    isTradingCondn2 = False

                    trade_end_date = self.data.index[trading_interval+i-1]
                    trade_length_list.append(np.busday_count(trade_start_date.date(),trade_end_date.date()))

                    total_profit += profit
                    signal_list.append(0)

                    profit_list.append(profit)
                    profit_long_list.append(long_profit)
                    profit_short_list.append(short_profit)
                    percentage_return_list.append(percentage_return)
                    net_percentage_return_list.append(net_percentage_return)

                    #Change Check Variables Value
                    isTradingCondn2 = False
                    break
                else:
                    pass

                
            if stdresidual[-1] > 4:
                if isTradingCondn1:
                    profit,long_profit,short_profit,percentage_return,net_percentage_return = Exit1(stockx_closing_value,
                    stocky_closing_value,
                    lot_x,
                    lot_y,
                    margin_x,
                    margin_y,
                    self.long,
                    self.short,self.multiplier_x,
                    self.multiplier_y)
                    isTradingCondn1 = False

                    self.multiplier_x = 1
                    self.multiplier_y = 1


                    trade_end_date = self.data.index[trading_interval+i-1]
                    trade_length_list.append(np.busday_count(trade_start_date.date(),trade_end_date.date()))

                    total_profit += profit
                    signal_list.append(0)

                    profit_list.append(profit)
                    profit_long_list.append(long_profit)
                    profit_short_list.append(short_profit)
                    percentage_return_list.append(percentage_return)
                    net_percentage_return_list.append(net_percentage_return)

                    #Change Check Variables Value
                    isTradingCondn1 = False
                    stoplossTrigger1 = True

                else:
                    # signal_list.append("Stop Loss Triggered")
                    signal_list.append("")
                    stoplossTrigger1 = True
                

            elif stdresidual[-1] < -4:
                 
                if isTradingCondn2:
                    profit,long_profit,short_profit,percentage_return,net_percentage_return = Exit2(stockx_closing_value,
                    stocky_closing_value,
                    lot_x,
                    lot_y,
                    margin_x,
                    margin_y,
                    self.long,
                    self.short,self.multiplier_x,
                    self.multiplier_y)

                    self.multiplier_x = 1
                    self.multiplier_y = 1

                    isTradingCondn2 = False

                    trade_end_date = self.data.index[trading_interval+i-1]
                    trade_length_list.append(np.busday_count(trade_start_date.date(),trade_end_date.date()))

                    total_profit += profit
                    signal_list.append(0)

                    profit_list.append(profit)
                    profit_long_list.append(long_profit)
                    profit_short_list.append(short_profit)
                    percentage_return_list.append(percentage_return)
                    net_percentage_return_list.append(net_percentage_return)

                    #Change Check Variables Value
                    isTradingCondn2 = False
                    stoplossTrigger2 = True
                

                else:
                    # signal_list.append("Stop Loss Triggered")
                    signal_list.append("")
                    stoplossTrigger2 = True

            elif stdresidual[-1] > 2 and stdresidual[-1] <4 and coint<0.10 and (not stoplossTrigger1) and (not isTradingCondn1) and coint_list[-1]<0.1 and cor>0.9:
                #Change Check Variables
                isTradingCondn1 = True

                trade_start_date = self.data.index[trading_interval+i-1]
                trade_count += 1
                trade_list.append(trade_count)
                
                long,short,investment,net_investment,effective_margin_x,effective_margin_y,multiplier_x,multiplier_y,effective_investment_x,effective_investment_y = Entry1(stockx_closing_value,stocky_closing_value,lot_x,lot_y,margin_x,margin_y)
                
                self.multiplier_x = multiplier_x
                self.multiplier_y = multiplier_y

                self.long = long
                self.short = short

                signal_list.append("1")
                investment_list.append(investment)
                multiplier_list_x.append(self.multiplier_x)
                multiplier_list_y.append(self.multiplier_y)
                effective_investment_x_list.append(effective_investment_x)
                effective_investment_y_list.append(effective_investment_y)
                net_investment_list.append(net_investment)
                effective_margin_list_x.append(effective_margin_x)
                effective_margin_list_y.append(effective_margin_y)


            elif stdresidual[-1] <-2 and stdresidual[-1] >-4 and coint<0.10 and (not stoplossTrigger2) and (not isTradingCondn2) and coint_list[-1]<0.1 and cor>0.9:
                #Change Check Variables
                isTradingCondn2 = True
                trade_start_date = self.data.index[trading_interval+i-1]
                trade_count += 1
                trade_list.append(trade_count)
                
                long,short,investment,net_investment,effective_margin_x,effective_margin_y,multiplier_x,multiplier_y,effective_investment_x,effective_investment_y = Entry2(stockx_closing_value,stocky_closing_value,lot_x,lot_y,margin_x,margin_y)
                
                self.multiplier_x = multiplier_x
                self.multiplier_y = multiplier_y

                self.long = long
                self.short = short


                signal_list.append("-1")
                investment_list.append(investment)
                multiplier_list_x.append(self.multiplier_x)
                multiplier_list_y.append(self.multiplier_y)
                effective_investment_x_list.append(effective_investment_x)
                effective_investment_y_list.append(effective_investment_y)
                net_investment_list.append(net_investment)
                effective_margin_list_x.append(effective_margin_x)
                effective_margin_list_y.append(effective_margin_y)


            elif stdresidual[-1] < 1 and (isTradingCondn1 or stoplossTrigger1) :
                if isTradingCondn1:
                    profit,long_profit,short_profit,percentage_return,net_percentage_return = Exit1(stockx_closing_value,
                    stocky_closing_value,
                    lot_x,
                    lot_y,
                    margin_x,
                    margin_y,
                    self.long,
                    self.short,self.multiplier_x,
                    self.multiplier_y)
                    isTradingCondn1 = False

                    self.multiplier_x = 1
                    self.multiplier_y = 1

                    trade_end_date = self.data.index[trading_interval+i-1]

                    print(self.data)
                    print(trade_end_date)
                    print(trade_start_date)
                    print("Hello")
                    trade_length_list.append(np.busday_count(trade_start_date.date(),trade_end_date.date()))

                    total_profit += profit
                    signal_list.append(0)

                    profit_list.append(profit)
                    profit_long_list.append(long_profit)
                    profit_short_list.append(short_profit)
                    percentage_return_list.append(percentage_return)
                    net_percentage_return_list.append(net_percentage_return)
                
                elif stoplossTrigger1:
                    stoplossTrigger1 = False
                    # signal_list.append("Stop Loss Reset")
                    signal_list.append("")

                else:
                    signal_list.append("")

            elif stdresidual[-1] > -1 and (isTradingCondn2 or stoplossTrigger2):
                if isTradingCondn2:
                    profit,long_profit,short_profit,percentage_return,net_percentage_return = Exit2(stockx_closing_value,
                    stocky_closing_value,
                    lot_x,
                    lot_y,
                    margin_x,
                    margin_y,
                    self.long,
                    self.short,
                    self.multiplier_x,
                    self.multiplier_y)

                    self.multiplier_x = 1
                    self.multiplier_y = 1

                    isTradingCondn2 = False

                    trade_end_date = self.data.index[trading_interval+i-1]
                    trade_length_list.append(np.busday_count(trade_start_date.date(),trade_end_date.date()))
                    total_profit += profit
                    signal_list.append(0)

                    profit_list.append(profit)
                    profit_long_list.append(long_profit)
                    profit_short_list.append(short_profit)
                    percentage_return_list.append(percentage_return)
                    net_percentage_return_list.append(net_percentage_return)

                
                elif stoplossTrigger2:
                    # signal_list.append("Stop Loss Reset")
                    signal_list.append("")
                    stoplossTrigger2 = False

                else:
                    signal_list.append("")

            else:
                signal_list.append("")


        df = pd.DataFrame()
        df["Dates"] = date_list
        df[f"{self.stocky} Y"] = stocky_closing_value_list
        df[f"{self.stockx} X"] = stockx_closing_value_list
        df["Standard Residual"] = stdresidual_list
        df["Residual"] = residual_list
        df["Y Predicted"] = ypred_list
        df["Signal"] = signal_list
        df["Coint"] = coint_list
        df["Correlation"] = corr_list

        df2 = pd.DataFrame()
        df3 = pd.DataFrame()
        df1 = pd.DataFrame()
        df1["Trades"] = trade_list
        df2["Trade Length"] = trade_length_list
        df2["Percentage Return"] = percentage_return_list
        df1["Investments"] = investment_list
        df1["Net Investments"] = net_investment_list
        df2["Profit"] = profit_list
        df2["Net Percentage Return"] = net_percentage_return_list
        df2["Long Profit"] = profit_long_list
        df2["Short Profit"] = profit_short_list
        df2[f"Effective Investment of {self.stockx} X"] = effective_investment_x_list
        df2[f"Effective Investment of {self.stocky} Y"] = effective_investment_y_list
        df1[f"Effective Margin of {self.stockx} X"] = effective_margin_list_x
        df1[f"Effective Margin of {self.stocky} Y"] = effective_margin_list_y
        df2["Multiplier X"] = multiplier_list_x
        df2["Multiplier Y"] = multiplier_list_y


        # df3["Total Invested"] = 
        # df3["Total Percentage Return"]
        output = pd.concat([df,df1,df2],axis=1)
        output = output.set_index("Dates")
        output['Trades'][trade_count+5]= "Individual Breakup"
        output['Trades'][trade_count+6] = f"Margin of {self.stockx} X"
        output['Trades'][trade_count+7] = self.marginx
        output['Investments'][trade_count+6] = f"Margin of {self.stocky} Y"
        output['Investments'][trade_count+7] = self.marginy

        output["Net Investments"][trade_count+5] =  f"Lot {self.stocky} Y"
        output["Net Investments"][trade_count+6] = self.lot_size_y
        output[f"Effective Margin of {self.stockx} X"][trade_count+5] = f"Lot  {self.stockx} X"
        output[f"Effective Margin of {self.stockx} X"][trade_count+6] = self.lot_size_x
        output[f"Effective Margin of {self.stocky} Y"][trade_count+5] = "Total Profit"
        output[f"Effective Margin of {self.stocky} Y"][trade_count+6] = total_profit
        output["Trade Length"][trade_count+5] = "Total Trade" 
        output["Trade Length"][trade_count+6] = trade_count

        print(total_profit)
        return output,total_profit

    def MakeGraph(self):
        df = pd.DataFrame([self.data[self.stockx][self.past_check_interval*self.data_length:self.time_interval*self.data_length],self.data[self.stocky][self.past_check_interval*self.data_length:self.time_interval*self.data_length]])
        df = df.T
        # print(df/df.iloc[0,:])
        df = df/df.iloc[0,:]
        print(df)
        ax = df.plot(title="Graph", fontsize=12, figsize=(20, 20))
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        
        #plt.figure(figsize=(20, 10), dpi= 120, facecolor='w', edgecolor='k')
        plt.title('Relative price change')
        plt.legend(loc='upper left', fontsize=12)
        plt.tight_layout()
        plt.style.use('bmh')
        plt.grid(True)
        return plt

# X label all dates are individual
# Markers for Buy and Short
# Markers for Square off
# Increase Resolution

# source env/Scripts/activate
# python Backtest_Implementation.py