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
    past_check_year,
    past_check_month,
     trading_year_start,
     trading_month_start,
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
        self.past_check_year = past_check_year
        self.past_check_month = past_check_month
        self.trading_year_start =  trading_year_start
        self.trading_month_start = trading_month_start
        self.capital = capital
        self.comission = comission
        self.margin1 = margin1
        self.margin2 = margin2
        self.trading_start_index = 0


    def collectData_Fyers(self):
        # Define the path to the data folder
        data_folder = os.path.join(os.getcwd(), 'Data', 'Fyers', f'{self.data_interval}_Data')
        
        # Load the data for stock1 and stock2 from the respective Excel files
        stock1_file = os.path.join(data_folder, f'{self.stock1}.xlsx')
        stock2_file = os.path.join(data_folder, f'{self.stock2}.xlsx')

        # Read the data from the 'Close' column of each file
        stock1_data = pd.read_excel(stock1_file, usecols=['close'])
        stock2_data = pd.read_excel(stock2_file, usecols=['close'])
        stock_date = pd.read_excel(stock1_file, usecols=['date'])

        # Remove ' IST' from date strings and convert to datetime
        stock_date['date'] = stock_date['date'].str.replace(' IST', '')
        stock_date['date'] = pd.to_datetime(stock_date['date'], format='%Y-%m-%d %H:%M:%S')

        # Combine the date with the stock data
        self.data = pd.concat([stock_date, stock1_data, stock2_data], axis=1)
        
        # Rename columns to stock names
        self.data.columns = ['Date', self.stock1, self.stock2]

        # Create a combined condition to filter data from the specified year and month onwards
        filter_condition = (self.data['Date'] >= pd.Timestamp(self.past_check_year, self.past_check_month, 1))
        self.data = self.data[filter_condition]

        # Set 'Date' as the index
        self.data.set_index('Date', inplace=True)

        # Handle missing data
        self.data.fillna(method='ffill', inplace=True)  # Forward fill
        self.data.fillna(method='bfill', inplace=True)  # Backward fill

        # Calculate the length of the data
        self.total_data_length = len(self.data)

        # Find the index of the first entry that matches trading_year_start and trading_month_start
        match_condition = (self.data.index >= pd.Timestamp(self.trading_year_start, self.trading_month_start, 1))
        first_matching_index = self.data[match_condition].index[0] if not self.data[match_condition].empty else None
        self.trading_start_index = self.data.index.get_loc(first_matching_index) if first_matching_index is not None else None

        # Print the data for verification
        print(self.data)
        print(self.trading_start_index," trading start index")
        
        return









    def checkPast(self):
        df = pd.DataFrame() 
    
        stockx,stocky,stdresidual,residual,ypred,condn,model,coint = LinearRegression(self.data[0:self.trading_start_index],self.stock1,self.stock2,False,True)
        self.condn = condn
        self.stockx = stockx
        self.stocky = stocky
        df[f"{stocky} Y"] = self.data[stocky][0:self.trading_start_index]
        df[f"{stockx} X"] = self.data[stockx][0:self.trading_start_index]
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
        # trading_interval = self.past_check_interval*self.data_length


        for i in range(1,self.total_data_length-self.trading_start_index+1):
            
            stockx,stocky,stdresidual,residual,ypred,coint = LinearRegression(self.data[i:self.trading_start_index+i],self.stock1,self.stock2,True,self.condn)
           
            corr_data = self.data[i:self.trading_start_index+i]
            cor = corr_data[self.stock1].corr(corr_data[self.stock2])
            corr_list.append(cor)


            stockx_closing_value = self.data[stockx][self.trading_start_index+i-1]
            stocky_closing_value = self.data[stocky][self.trading_start_index+i-1]
            stockx_closing_value_list.append(stockx_closing_value)
            stocky_closing_value_list.append(stocky_closing_value)
            stdresidual_list.append(stdresidual[-1])
            residual_list.append(residual[-1]) 
            ypred_list.append(ypred[-1])
            coint_list.append(coint)
            date_list.append(self.data.index[self.trading_start_index+i-1])

            if i == self.total_data_length-self.trading_start_index-1:
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

                    trade_end_date = self.data.index[self.trading_start_index+i-1]
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

                    trade_end_date = self.data.index[self.trading_start_index+i-1]
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


                    trade_end_date = self.data.index[self.trading_start_index+i-1]
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

                    trade_end_date = self.data.index[self.trading_start_index+i-1]
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

            elif stdresidual[-1] > 2 and stdresidual[-1] <4 and coint<0.10 and (not stoplossTrigger1) and (not isTradingCondn1) and coint_list[-1]<0.1  and cor>0.9:
                #Change Check Variables
                isTradingCondn1 = True

                trade_start_date = self.data.index[self.trading_start_index+i-1]
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
                trade_start_date = self.data.index[self.trading_start_index+i-1]
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

                    trade_end_date = self.data.index[self.trading_start_index+i-1]

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

                    trade_end_date = self.data.index[self.trading_start_index+i-1]
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