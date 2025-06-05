import statsmodels.api as sm
from scipy import stats
from statsmodels.tsa.stattools import adfuller

def LinearRegression(data,stock1,stock2,voluntary_check,other_check):
    condn = False
    xdata = data[stock1]
    ydata = data[stock2]
    #Doing Linear Regression
    model1 = sm.OLS(ydata, sm.add_constant(xdata)).fit()  #LR where target varible (y) =ydata , which we wanna predict and xdata is independent variables 
    result1 = stats.linregress(xdata, ydata)
    std_err1 = result1.intercept_stderr  # taking out Standard error of the intercept which represents the variability or uncertainty associated with the estimated intercept of the regression line. It tells you how much the intercept might fluctuate if you were to perform the regression on different samples of the same data

    influence1 = model1.get_influence() #It calculates the influence of each data point on the model's estimates.
    standardized_residuals1 = influence1.resid #Standardized residuals are a common way to assess how well individual data points fit the overall regression line. They are calculated by taking the regular residuals (the difference between the actual y-value and the predicted y-value for each data point) and dividing them by an estimate of the standard deviation of the error term in the model
    res_err1 = standardized_residuals1.std()
    std_res1 = influence1.resid_studentized_internal
    ypred1 = model1.predict(sm.add_constant(xdata))
    

    rat1 = std_err1/res_err1

    model2 = sm.OLS(xdata, sm.add_constant(ydata)).fit()
    result2 = stats.linregress(ydata, xdata)
    std_err2 = result2.intercept_stderr
    influence2 = model2.get_influence()
    standardized_residuals2 = influence2.resid
    res_err2 = standardized_residuals2.std()
    std_res2 = influence2.resid_studentized_internal
    ypred2 = model2.predict(sm.add_constant(ydata))


    rat2 = std_err2/res_err2

    #Output
    if rat1 < rat2:
        stdresidual = std_res1
        residual = standardized_residuals1
        ypred = ypred1
        stockx = stock1
        stocky = stock2
        adfTest = adfuller(standardized_residuals1, autolag='AIC')

        # print(model1.summary())
        # print(model1.rsquared)
        # cor = data[stock1].corr(data[stock2])
        # print(cor)
        model = model1
        condn = True

    else:

        stdresidual = std_res2
        residual = standardized_residuals2
        ypred = ypred2
        stockx = stock2
        stocky = stock1
        model = model2
        adfTest = adfuller(standardized_residuals2, autolag='AIC')
        # print(model2.summary())
        # print(model2.rsquared)

        # cor = data[stock1].corr(data[stock2])
        # print(cor)

    if voluntary_check:
        if other_check:
            stdresidual = std_res1
            residual = standardized_residuals1
            ypred = ypred1
            stockx = stock1
            stocky = stock2
            adfTest = adfuller(standardized_residuals1, autolag='AIC')
        else:
            stdresidual = std_res2
            residual = standardized_residuals2
            ypred = ypred2
            stockx = stock2
            stocky = stock1
            adfTest = adfuller(standardized_residuals2, autolag='AIC')
        return (stockx,stocky,stdresidual,residual,ypred,adfTest[1])



    return (stockx,stocky,stdresidual,residual,ypred,condn,model,adfTest[1])

