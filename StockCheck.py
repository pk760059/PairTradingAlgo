import yfinance as yf
import datetime
import pandas as pd
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
from scipy import stats

# YEARS MONTH DAY
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=2*365)

def StockCheck(stock1,stock2):
    try:
        print(stock1,stock2)
        data = yf.download(stock1+" "+stock2, start=start_date, end=end_date)
        
        # Take closing Value only
        data = data["Close"]
        data.fillna(method = 'ffill', inplace= True)
        data.fillna(method = 'bfill', inplace= True)


        # Ratio Calculation
        data['ratio'] = data[stock1]/data[stock2]
        # Corelation Calculation
        cor = data[stock1].corr(data[stock2])

        xdata = data[stock1]
        ydata = data[stock2]

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
        else:
            adfTest = adfuller(standardized_residuals_yx, autolag='AIC')
            beta = result_yx.slope
            intercept = result_yx.intercept
            std_residual = residualerror_yx
            lastest_stdresidual = stdres_yx[-1]
            lastest_residual = standardized_residuals_yx[-1]


        return(beta,intercept,std_residual,lastest_stdresidual,lastest_residual,cor,adfTest[1])

    except Exception as e:
        print(e)
        return(0,0,0,0,0,0,0)

company1=[]
company2=[]
Sector = []
P_values=[]
beta_values=[]
intercept_values=[]
std_residual_values=[]
lastest_stdresidual_values=[]
lastest_residual_values=[]
cor_values=[]


data=pd.read_csv("Input/FNO_LIST.csv")
from itertools import combinations 

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
for i in list(resultList)[0:] :

    beta,intercept,std_residual,lastest_stdresidual,lastest_residual,cor,adfTest = StockCheck(i[0],i[1])

    if adfTest<0.10 and cor>0.88:     
        company1.append(i[0])
        company2.append(i[1])
        Sector.append(i[2])
        beta_values.append(beta)
        intercept_values.append(intercept)
        std_residual_values.append(std_residual)
        lastest_stdresidual_values.append(lastest_stdresidual)
        lastest_residual_values.append(lastest_residual)
        cor_values.append(cor)
        P_values.append(adfTest)
        
pd1 = pd.DataFrame()
pd1['Company2 (Y)'] = company2
pd1['Company1 (X)'] = company1
pd1['Sector'] = Sector
pd1['P-value']=P_values
pd1['beta']=beta_values
pd1['intercept']=intercept_values
pd1['std_residual']=std_residual_values
pd1['Normalised_residual']=lastest_stdresidual_values
pd1['Error for that day']=lastest_residual_values
pd1['Correlation']=cor_values

pd1.to_csv('Output/Stocks.csv')

