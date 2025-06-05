import math

def Entry1(closex,closey,lotx,loty,marginx,marginy):
    #Y short
    #X long

    multiplier_x = 1
    multiplier_y = 1

    long = closex
    short = closey

    effective_investment_x = long*lotx
    effective_investment_y = short*loty

    if effective_investment_x > effective_investment_y:
        rat = effective_investment_x/effective_investment_y
        if rat>1.5:
            rat = rat+0.51
            multiplier_y = math.floor(rat)
        else:
            multiplier_y = 1

        investment = long*lotx + short*loty*multiplier_y
        effective_investment_y = effective_investment_y*multiplier_y

        net_investment = (long*lotx*marginx)/100 + (short*loty*marginy*multiplier_y)/100
        effective_margin_x = (long*lotx*marginx)/100
        effective_margin_y = (short*loty*marginy*multiplier_y)/100
        
        
    
    else:
        rat = effective_investment_y/effective_investment_x
        if rat>1.5:
            rat = rat+0.51
            multiplier_x = math.floor(rat)
        else:
            multiplier_x = 1

        investment = long*lotx*multiplier_x + short*loty
        effective_investment_x = effective_investment_x*multiplier_x

        net_investment = (long*lotx*marginx*multiplier_x)/100 + (short*loty*marginy)/100
        effective_margin_x = (long*lotx*marginx*multiplier_x)/100
        effective_margin_y = (short*loty*marginy)/100




    return long,short,investment,net_investment,effective_margin_x,effective_margin_y,multiplier_x,multiplier_y,effective_investment_x,effective_investment_y


def Entry2(closex,closey,lotx,loty,marginx,marginy):
    #X short
    #Y long


    multiplier_x = 1
    multiplier_y = 1

    long = closey
    short = closex

    effective_investment_y = long*loty
    effective_investment_x = short*lotx

    if effective_investment_x > effective_investment_y:
        rat = effective_investment_x/effective_investment_y
        if rat>1.5:
            rat = rat+0.51
            multiplier_y = math.floor(rat)
        else:
            multiplier_y = 1

        investment = long*loty*multiplier_y + short*lotx
        net_investment = (long*loty*marginy*multiplier_y)/100 + (short*lotx*marginx)/100
        effective_investment_y = effective_investment_y*multiplier_y
        effective_margin_x = (short*lotx*marginx)/100
        effective_margin_y = (long*loty*marginy*multiplier_y)/100

    else:
        rat = effective_investment_y/effective_investment_x
        if rat>1.5:
            rat = rat+0.51
            multiplier_x = math.floor(rat)
        else:
            multiplier_x = 1

        investment = long*loty + short*lotx*multiplier_x
        net_investment = (long*loty*marginy)/100 + (short*lotx*marginx*multiplier_x)/100
        effective_investment_x = effective_investment_x * multiplier_x
        effective_margin_x = (short*lotx*marginx*multiplier_x)/100
        effective_margin_y = (long*loty*marginy)/100


    return long,short,investment,net_investment,effective_margin_x,effective_margin_y,multiplier_x,multiplier_y,effective_investment_x,effective_investment_y



def Exit1(closex,closey,lotx,loty,marginx,marginy,long,short,multiplier_x,multiplier_y):
    profit = (closex-long)*lotx*multiplier_x + (short-closey)*loty*multiplier_y
    short_profit = (short-closey)*loty*multiplier_y
    long_profit = (closex-long)*lotx*multiplier_x


    investment = long*lotx*multiplier_x + short*loty*multiplier_y
    net_investment = (long*lotx*marginx*multiplier_x)/100 + (short*loty*marginy*multiplier_y)/100


    percentage_return = (profit/investment)*100
    net_percentage_return = (profit/net_investment)*100


    return (profit,long_profit,short_profit,percentage_return,net_percentage_return)

def Exit2(closex,closey,lotx,loty,marginx,marginy,long,short,multiplier_x,multiplier_y):
    profit = (closey-long)*loty*multiplier_y + (short-closex)*lotx*multiplier_x
    short_profit = (short-closex)*lotx*multiplier_x
    long_profit = (closey-long)*loty*multiplier_y
    investment = long*loty*multiplier_y + short*lotx*multiplier_x
    net_investment = long*loty*(marginy/100)*multiplier_y + short*lotx*(marginx/100)*multiplier_x
    percentage_return = (profit/investment)*100
    net_percentage_return = (profit/net_investment)*100
    
    return (profit,long_profit,short_profit,percentage_return,net_percentage_return)