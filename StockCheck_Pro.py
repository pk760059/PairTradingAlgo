import yfinance as yf
import datetime
import pandas as pd

from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
from scipy import stats
from itertools import combinations
import threading
import queue



end_date = datetime.datetime.now()#1st jan 2020
start_date = end_date - datetime.timedelta(days=2*365)


# data = pd.read_csv("Input/FNO_LIST.csv")
data = pd.read_csv(r"C:\Users\pramo\Documents\GitHub\PairTrader\Input\FNO_LIST.csv")
grouped = data.groupby('Sector')
resultList = []
for key, group in grouped:

    # Make it optimised in making pairs

    for b, g in combinations(group['SYMBOLS'].tolist(), 2):
        resultList.append([b, g, key])
        
resultList.sort()

total_list=resultList

def cheg_list(total_list):
    
    '''
    Checks all pairs and returns list of pair with corr more than 0.84
    '''

    rlist=[]
    for all_list in total_list:
        s1=all_list[0]
        s2=all_list[1]
        
        # df = yf.download(s1+" "+s2, start=start_date, end=end_date)
        # df = df["Close"]
        df=pd.read_csv(fr"C:\Users\pramo\Documents\GitHub\PairTrader\Data\Yt Stock Data\{s1}_{s2}_StoredData.csv")
        cor = df[s1].corr(df[s2])
        if cor>0.84:
            rlist.append(all_list)
    return rlist

stime2 = datetime.datetime.now()

mliys=cheg_list(total_list) #sorted list with all pairs with corr >0.84

etime2 = datetime.datetime.now()

def StockCheck(mlist,results_queue):
    stock1=mlist[0]
    stock2=mlist[1]
    # print(f"\n Start for {mlist}\n")
    data=pd.read_csv(fr"C:\Users\pramo\Documents\GitHub\PairTrader\Data\Yt Stock Data\{stock1}_{stock2}_StoredData.csv")
    try:
        # Ratio Calculation
        data['ratio'] = data[stock1]/data[stock2]
        # Corelation Caculation
        cor = data[stock1].corr(data[stock2])
        if cor < 0.88:
            results_queue.put([None, None, None, None, None, None, None, None, None, None])
            return 
        
        xdata = data[stock1]
        ydata = data[stock2]
        latestx = xdata.iloc[-1]
        latesty = ydata.iloc[-1]

        # Calculate Intercept Standard Error
        result_xy = stats.linregress(xdata, ydata)
        stder_xy = result_xy.intercept_stderr
        result_yx = stats.linregress(ydata, xdata)
        stder_yx = result_xy.intercept_stderr


        # First part
        # We use Ordinary Least Squares method to find the line of best fit
        model_xy = sm.OLS(ydata, sm.add_constant(xdata)).fit()
        influence_xy = model_xy.get_influence()
        standardized_residuals_xy = influence_xy.resid
        residualerror_xy = standardized_residuals_xy.std()
        stdres_xy = influence_xy.resid_studentized_internal
        rat_xy = stder_xy/residualerror_xy
                
        #Outputs

        # Part 2
        model_yx = sm.OLS(xdata, sm.add_constant(ydata)).fit()
        influence_yx = model_yx.get_influence()
        standardized_residuals_yx = influence_yx.resid
        residualerror_yx = standardized_residuals_yx.std()
        stdres_yx = influence_yx.resid_studentized_internal
        rat_yx = stder_yx/residualerror_yx

        # Outputs
        # if first regression is smaller
        if rat_xy < rat_yx:
            adfTest = adfuller(standardized_residuals_xy, autolag='AIC')
            beta = result_xy.slope
            intercept = result_xy.intercept
            std_residual = residualerror_xy
            lastest_stdresidual = stdres_xy[-1]
            lastest_residual = standardized_residuals_xy[-1]
            ratio = (1-(abs(intercept)/latesty))*100
            # print(cor)
            
            stk1=stock1
            stk2=stock2
            
            
            # results_queue.put([beta, intercept, std_residual, lastest_stdresidual, lastest_residual, cor, adfTest[1], ratio, stock1, stock2])

        else:
            adfTest = adfuller(standardized_residuals_yx, autolag='AIC')
            beta = result_yx.slope
            intercept = result_yx.intercept
            std_residual = residualerror_yx
            lastest_stdresidual = stdres_yx[-1]
            lastest_residual = standardized_residuals_yx[-1]
            ratio = (1-(abs(intercept)/latestx))*100
            # print(cor)
            
            stk1=stock2
            stk2=stock1
            
            
            # results_queue.put([beta, intercept, std_residual, lastest_stdresidual, lastest_residual, cor, adfTest[1], ratio, stock2, stock1])
            
        # print(f"\nSuccess for  {mlist}\n")
        if adfTest[1]<0.10 and cor>0.88:
            # results_queue.put([beta, intercept, std_residual, lastest_stdresidual, lastest_residual, cor, adfTest[1], ratio, stock1, stock2])
            results_queue.put([stk2,stk1,mlist[2],adfTest[1],beta,intercept,std_residual, lastest_stdresidual, lastest_residual,cor,ratio])
        else:
            tlist=[stock1,stock2]
            # if tlist in [['INDUSINDBK.NS', 'AXISBANK.NS'],['AXISBANK.NS', 'RBLBANK.NS'],['BOSCHLTD.NS', 'EXIDEIND.NS'],['HINDPETRO.NS', 'BPCL.NS'],['HCLTECH.NS', 'BSOFT.NS'],['OBEROIRLTY.NS', 'DLF.NS'],['ICICIGI.NS', 'SBILIFE.NS'],['TATAPOWER.NS', 'TATASTEEL.NS']]:
            print(f'{tlist}\n adf-> {adfTest[1]} cor -> {cor}\n ------------ ')
            results_queue.put([None, None, None, None, None, None, None, None, None, None])
    except:
        print(f'Error in {mlist} ' )    
stime = datetime.datetime.now()

results_queue = queue.Queue()
threads = []
for duration in mliys:
    # print(duration)
    thread = threading.Thread(target=StockCheck, args=(duration,results_queue))
    
    threads.append(thread)
    thread.start()

etime = datetime.datetime.now()



for thread in threads:
    thread.join()
    
results = []
while not results_queue.empty():
    result = results_queue.get()
    results.append(result)
    
    
    
dffin = pd.DataFrame(results,columns=['Company2 (Y)','Company1 (X)','Sector','P-value','beta','intercept','std_residual','Normalised_residual','Error for that day','Correlation','ratio'])
# print(dffin)# df with none values

fdffin=dffin.dropna(how='any')



fdffin.to_csv(r'C:\Users\pramo\Documents\GitHub\PairTrader\Output\New_Stocks_after_threading2.csv')
print(f"It took {etime2-stime2} seconds to make the list \nand {etime-stime} seconds to perform analysis on {len(resultList)} pairs.")