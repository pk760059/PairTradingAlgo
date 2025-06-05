import yfinance as yf
import datetime
import pandas as pd
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
from scipy import stats
from itertools import combinations
import multiprocessing as mp

 
# YEARS MONTH DAY
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=1*365)

# Define global lists to be shared among processes
def init_manager():
    manager = mp.Manager()
    shared_lists = {
        'company1': manager.list(),
        'company2': manager.list(),
        'Sector': manager.list(),
        'P_values': manager.list(),
        'beta_values': manager.list(),
        'intercept_values': manager.list(),
        'std_residual_values': manager.list(),
        'lastest_stdresidual_values': manager.list(),
        'lastest_residual_values': manager.list(),
        'cor_values': manager.list(),
        'ratios': manager.list()
    }
    return shared_lists

def StockCheck(stock_pair):
    stock1, stock2, sector = stock_pair

    try:
        print(stock1,stock2)
        # data = yf.download(stock1+" "+stock2, start=start_date, end=end_date)
        # data=pd.read_csv(fr"C:\Users\arshm\OneDrive\Desktop\Py\Pair_T\PairTrader\Data\Yt Stock Data\{stock1}_{stock2}_StoredData.csv")

        # # Take closing Value only
        # # data = data["Close"]

        # data.fillna(method = 'ffill', inplace= True)
        # data.fillna(method = 'bfill', inplace= True)
       
       
        # Paths to the stock data files
       
        file_path_stock1 = fr"C:\Users\arshm\OneDrive\Desktop\Py\Pair_T\PairTrader\Data\Fyers\30_Data\{stock1}.xlsx"
        file_path_stock2 = fr"C:\Users\arshm\OneDrive\Desktop\Py\Pair_T\PairTrader\Data\Fyers\30_Data\{stock2}.xlsx"

        # Read the data from each file
        data_stock1 = pd.read_excel(file_path_stock1, sheet_name="Sheet1")
        data_stock2 = pd.read_excel(file_path_stock2, sheet_name="Sheet1")

        # Convert the 'Date' column to datetime format
        data_stock1['date'] = pd.to_datetime(data_stock1['date'], format='%Y-%m-%d %H:%M:%S IST')
        data_stock2['date'] = pd.to_datetime(data_stock2['date'], format='%Y-%m-%d %H:%M:%S IST')

        # Filter the data based on start_date
        data_stock1 = data_stock1[data_stock1['date'] >= start_date]
        data_stock2 = data_stock2[data_stock2['date'] >= start_date]
        
        # print(data_stock1, data_stock2)

        # Extract the 'Close' column
        data_stock1 = data_stock1['close']
        data_stock2 = data_stock2['close']

        # Merge the two DataFrames on the 'Date' column
        data = pd.DataFrame({
            f'{stock1}': data_stock1,
            f'{stock2}': data_stock2
        })

        # Forward fill and backward fill any missing values
        data.fillna(method='ffill', inplace=True)
        data.fillna(method='bfill', inplace=True)

        # Ratio Calculation
        data['ratio'] = data[stock1]/data[stock2]
        # Corelation Caculation
        cor = data[stock1].corr(data[stock2])
        if cor < 0.88:
            return None, None, None, None, None, None, None, None, None, None, None
        
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
            return (beta, intercept, std_residual, lastest_stdresidual, lastest_residual, cor, adfTest[1], ratio, stock1, stock2,sector)
        else:
            adfTest = adfuller(standardized_residuals_yx, autolag='AIC')
            beta = result_yx.slope
            intercept = result_yx.intercept
            std_residual = residualerror_yx
            lastest_stdresidual = stdres_yx[-1]
            lastest_residual = standardized_residuals_yx[-1]
            ratio = (1-(abs(intercept)/latestx))*100
            return (beta, intercept, std_residual, lastest_stdresidual, lastest_residual, cor, adfTest[1], ratio, stock2, stock1,sector)
            
    except Exception as e:
        print(e)
        return(0,0,0,0,0,0,0,0,0,0,0)
    
def process_results(result, shared_lists):
    beta, intercept, std_residual, lastest_stdresidual, lastest_residual, cor, adfTest, ratio, stock1, stock2,sector = result
    if cor is None:
        return
    if adfTest < 0.10 and cor > 0.88:
        shared_lists['company1'].append(stock1)
        shared_lists['company2'].append(stock2)
        shared_lists['Sector'].append(sector)
        shared_lists['beta_values'].append(beta)
        shared_lists['intercept_values'].append(intercept)
        shared_lists['std_residual_values'].append(std_residual)
        shared_lists['lastest_stdresidual_values'].append(lastest_stdresidual)
        shared_lists['lastest_residual_values'].append(lastest_residual)
        shared_lists['cor_values'].append(cor)
        shared_lists['P_values'].append(adfTest)
        shared_lists['ratios'].append(ratio)

# for i in list(resultList)[0:] :

#     beta,intercept,std_residual,lastest_stdresidual,lastest_residual,cor,adfTest, ratio, x_axis, y_axis = StockCheck(i[0],i[1])    
#     #print(cor)
#     if cor == None:
#         continue

#     if adfTest<0.10 and cor>0.88:     
#         company1.append(x_axis)
#         company2.append(y_axis)
#         Sector.append(i[2])
#         beta_values.append(beta)
#         intercept_values.append(intercept)
#         std_residual_values.append(std_residual)
#         lastest_stdresidual_values.append(lastest_stdresidual)
#         lastest_residual_values.append(lastest_residual)
#         cor_values.append(cor)
#         P_values.append(adfTest)
#         ratios.append(ratio)

if __name__ == '__main__':
    
    shared_lists = init_manager()#Global lists for multiprocesssing

    stime = datetime.datetime.now()
    # data = pd.read_csv("Input/FNO_LIST.csv")
    data = pd.read_csv(r"C:\Users\arshm\OneDrive\Desktop\Py\Pair_T\PairTrader\Input\FNO_LIST.csv")


    # group all the data based on sector and store it in grouped data
    grouped = data.groupby('Sector')
    resultList = []

    #key = Sector and group = Data of that sector
    # key is Example IT
    # group is the symbol of that key
    for key, group in grouped:

        # Make it optimised in making pairs

        for b, g in combinations(group['SYMBOLS'].tolist(), 2):
            resultList.append([b, g, key])

    resultList.sort()   




    # Use multiprocessing to process the stock pairs
    with mp.Pool(20) as pool:
        for result in pool.map(StockCheck, resultList):
            sector = result[2]
            process_results(result,shared_lists)
            
    
    pd1 = pd.DataFrame({
        'Company2 (Y)': list(shared_lists['company2']),
        'Company1 (X)': list(shared_lists['company1']),
        'Sector': list(shared_lists['Sector']),
        'P-value': list(shared_lists['P_values']),
        'beta': list(shared_lists['beta_values']),
        'intercept': list(shared_lists['intercept_values']),
        'std_residual': list(shared_lists['std_residual_values']),
        'Normalised_residual': list(shared_lists['lastest_stdresidual_values']),
        'Error for that day': list(shared_lists['lastest_residual_values']),
        'Correlation': list(shared_lists['cor_values']),
        'ratio': list(shared_lists['ratios'])
    })

    # pd1.to_csv('Output/Stocks.csv') 
    pd1.to_csv(r'C:\Users\arshm\OneDrive\Desktop\Py\Pair_T\PairTrader\Output\Stocksnew_multi.csv')
    etime = datetime.datetime.now()
    print(f"{etime-stime} time taken to run script")