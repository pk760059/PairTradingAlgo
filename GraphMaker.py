import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

arr = os.listdir("Data/FinalBacktestData")


for j in range(len(arr)):

    data = pd.read_csv(f"Data/FinalBacktestData/{arr[j]}")


    stockx_long_markers = []
    stocky_short_markers = []
    stocky_long_markers = []
    stockx_short_markers = []
    square_off_markers_x = []
    square_off_markers_y = []



        

    # data[data.columns[0]] = pd.to_datetime(data[data.columns[0]], format='%Y-%m-%d')
    data[data.columns[1]] = data[data.columns[1]].astype(float)
    data[data.columns[2]] = data[data.columns[2]].astype(float)

    df = pd.DataFrame([data[data.columns[0]],data[data.columns[1]],data[data.columns[2]]])
    df = df.T
    df = df.set_index("Dates")




    df = (df)/(df.iloc[0,:])

    for i in range(len(df)):
        if float(data[data.columns[6]][i]) == 1:
            stockx_long_markers.append(df[df.columns[1]][i])
            stocky_short_markers.append(df[df.columns[0]][i])
            stocky_long_markers.append(float('nan'))        
            stockx_short_markers.append(float('nan'))
            square_off_markers_x.append(float('nan'))
            square_off_markers_y.append(float('nan'))
        
        elif float(data[data.columns[6]][i]) == -1:

            stockx_short_markers.append(df[df.columns[1]][i])
            stocky_long_markers.append(df[df.columns[0]][i])
            stockx_long_markers.append(float('nan'))
            stocky_short_markers.append(float('nan'))
            square_off_markers_x.append(float('nan'))
            square_off_markers_y.append(float('nan'))

            pass

        elif float(data[data.columns[6]][i]) == 0:
            # square_off_list.append(i+1)
            stockx_long_markers.append(float('nan'))
            stocky_short_markers.append(float('nan'))
            stockx_short_markers.append(float('nan'))
            stocky_long_markers.append(float('nan'))
            square_off_markers_x.append(df[df.columns[1]][i])
            square_off_markers_y.append(df[df.columns[0]][i])
            pass
        
        else:
            stockx_long_markers.append(float('nan'))
            stocky_short_markers.append(float('nan'))
            stockx_short_markers.append(float('nan'))
            stocky_long_markers.append(float('nan'))
            square_off_markers_x.append(float('nan'))
            square_off_markers_y.append(float('nan'))



    # ax = df.plot(title="Stock Prices", fontsize=12, figsize=(20, 20),markevery=[square_off_list,stockx_long_list],marker="o",markerfacecolor='black', markersize=6)
    # ax.set_xlabel("Date")
    # ax.set_ylabel("Price")
    # ax.plot(,stockx_long_list,marker="")
    # ax.plot([2,4,5,7,10],)
    # ax.plot(stockx_long_list,marker = "D")
    # ax.scatter(xp, float(df, marker="^", s=50)
    plt.figure(figsize=(10,10))
    plt.plot(df.index,df[df.columns[0]])
    plt.plot(df.index,df[df.columns[1]])

    plt.plot(df.index,stockx_long_markers,marker="^",markerfacecolor="green",markersize=12)
    plt.plot(df.index,stockx_short_markers,marker="v",markerfacecolor="red",markersize=12)
    plt.plot(df.index,stocky_long_markers,marker="^",markerfacecolor="green",markersize=12)
    plt.plot(df.index,stocky_short_markers,marker="v",markerfacecolor="red",markersize=12)
    plt.plot(df.index,square_off_markers_x,marker="o",markerfacecolor="black",markersize=12)
    plt.plot(df.index,square_off_markers_y,marker="o",markerfacecolor="black",markersize=12)
    plt.xticks(df.index[::40])

    #plt.figure(figsize=(20, 10), dpi= 120, facecolor='w', edgecolor='k')
    plt.title('Relative price change')
    plt.xlabel('Dates')
    plt.ylabel('Price')
    plt.legend([[df.columns[0]],[df.columns[1]]],loc='upper left', fontsize=12)
    # plt.tight_layout()
    # plt.style.use('bmh')
    plt.grid(True)
    # plt.show()
    file_name = f"{arr[j]}".replace(".csv","")
    plt.savefig(f"Data/FinalGraph/{file_name}")

    #06-01-2020