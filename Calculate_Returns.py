import pandas as pd
import os
import statistics
from datetime import datetime
import re

def calculateReturns2(stockyprev, stockxprev, stocky, stockx, lotx, loty, multiplier_x, multiplier_y):
    returns = (stockyprev - stocky) * loty * multiplier_y + (stockx - stockxprev) * lotx * multiplier_x
    return returns

def calculateReturns1(stockyprev, stockxprev, stocky, stockx, lotx, loty, multiplier_x, multiplier_y):
    returns = (stocky - stockyprev) * loty * multiplier_y + (stockxprev - stockx) * lotx * multiplier_x
    return returns

def Mega_s(df, w1, w2):
    if df.empty:
        print("Empty DataFrame provided.")
        return

    for col in df.columns:
        if col.startswith(w1) and col.endswith(w2):
            return None, col 
        
        if df[col].dtype == object:
            filtered_df = df[df[col].str.startswith(w1) & df[col].str.endswith(w2)]
            if not filtered_df.empty:
                for index, row in filtered_df.iterrows():
                    return index, col

def calculate_returns(filepath):
    isTrading1 = False
    isTrading2 = False
    tradeNumber = 0
    risk_free_rate = 0

    data = pd.read_csv(filepath)
    print(f"Processing file: {filepath}")

    r1, c1 = Mega_s(data.copy(), 'Margin', 'X')
    r2, c2 = Mega_s(data.copy(), 'Margin', 'Y')
    r3, c3 = Mega_s(data.copy(), 'Lot', 'Y')
    r4, c4 = Mega_s(data.copy(), 'Lot', 'X')
    
    marginx = float(data[c1][r1+1])
    marginy = float(data[c2][r2+1])
    loty = float(data[c3][r3+1])
    lotx = float(data[c4][r4+1])

    ParentReturnsList = []
    returnsList = []
    percentage_returns_list = []
    stockyprev = 0
    stockxprev = 0

    for i in range(len(data)):
        if float(data[data.columns[6]][i]) == 0:
            if isTrading2:
                stocky = float(data[data.columns[1]][i])
                stockx = float(data[data.columns[2]][i])
                r7, c7 = Mega_s(data.copy(), 'Multiplier', 'X')
                r8, c8 = Mega_s(data.copy(), 'Multiplier', 'Y')
                multiplier_x = float(data[c7][tradeNumber])
                multiplier_y = float(data[c8][tradeNumber])
                returns = calculateReturns2(stockyprev, stockxprev, stocky, stockx, lotx, loty, multiplier_x, multiplier_y)
                percentage_returns = returns / float(data[data.columns[9]][tradeNumber])
                returnsList.append(returns)
                percentage_returns_list.append(percentage_returns)
                ParentReturnsList.append(returns)
            elif isTrading1:
                stocky = float(data[data.columns[1]][i])
                stockx = float(data[data.columns[2]][i])
                r5, c5 = Mega_s(data.copy(), 'Multiplier', 'X')
                r6, c6 = Mega_s(data.copy(), 'Multiplier', 'Y')
                multiplier_x = float(data[c5][tradeNumber])
                multiplier_y = float(data[c6][tradeNumber])
                returns = calculateReturns1(stockyprev, stockxprev, stocky, stockx, lotx, loty, multiplier_x, multiplier_y)
                percentage_returns = returns / float(data[data.columns[9]][tradeNumber])
                returnsList.append(returns)
                percentage_returns_list.append(percentage_returns)
                ParentReturnsList.append(returns)

            isTrading1 = False
            isTrading2 = False
            stockyprev = 0
            stockxprev = 0
            percentage_returns_list = []
            returnsList = []
            tradeNumber += 1
            continue

        elif float(data[data.columns[6]][i]) == 1:
            stockyprev = float(data[data.columns[1]][i])
            stockxprev = float(data[data.columns[2]][i])
            isTrading2 = True

        elif float(data[data.columns[6]][i]) == -1:
            stockyprev = float(data[data.columns[1]][i])
            stockxprev = float(data[data.columns[2]][i])
            isTrading1 = True

        if isTrading2:
            stocky = float(data[data.columns[1]][i])
            stockx = float(data[data.columns[2]][i])
            r9, c9 = Mega_s(data.copy(), 'Multiplier', 'X')
            r10, c10 = Mega_s(data.copy(), 'Multiplier', 'Y')
            multiplier_x = float(data[c9][tradeNumber])
            multiplier_y = float(data[c10][tradeNumber])
            returns = calculateReturns2(stockyprev, stockxprev, stocky, stockx, lotx, loty, multiplier_x, multiplier_y)
            percentage_returns = returns / float(data[data.columns[9]][tradeNumber])
            returnsList.append(returns)
            percentage_returns_list.append(percentage_returns)
            ParentReturnsList.append(returns)

        elif isTrading1:
            stocky = float(data[data.columns[1]][i])
            stockx = float(data[data.columns[2]][i])
            r11, c11 = Mega_s(data.copy(), 'Multiplier', 'X')
            r12, c12 = Mega_s(data.copy(), 'Multiplier', 'Y')
            multiplier_x = float(data[c11][tradeNumber])
            multiplier_y = float(data[c12][tradeNumber])
            returns = calculateReturns1(stockyprev, stockxprev, stocky, stockx, lotx, loty, multiplier_x, multiplier_y)
            percentage_returns = returns / float(data[data.columns[9]][tradeNumber])
            returnsList.append(returns)
            percentage_returns_list.append(percentage_returns)
            ParentReturnsList.append(returns)
        else:
            ParentReturnsList.append("")

    data.insert(7, 'Returns', ParentReturnsList)
    # output_filepath = os.path.join(os.path.dirname(filepath), 'new', os.path.basename(filepath))
    data.to_csv(filepath)
    print(f"File saved to: {filepath} with updated Returns")

