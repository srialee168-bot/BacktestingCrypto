import yfinance as yf
import pandas as pd
from datetime import timedelta
from colorama import Fore, Back, Style  #color texts


data = yf.download("SOL-USD", period="1mo", interval="1h", auto_adjust= False)

#checks if the yahoo finnace has a timezone 
if data.index.tz is None:
    data.index = data.index.tz_localize("UTC")
data.index = data.index.tz_convert("US/Pacific")
# Convert to LA time


# Flatten MultiIndex if exists
if isinstance(data.columns, pd.MultiIndex):
    data.columns = [col[0] for col in data.columns]

# EMA lines - used for determining uptrend or downtrend
data["EMA_20"] = data["Close"].ewm(span=20, adjust=False).mean()
data["EMA_50"] = data["Close"].ewm(span=50, adjust=False).mean()



cash = 10000  
shares = 0

long = False
short = False

# Backtest
for i in range(2, len(data)):
    price = data["Close"].iloc[i]
    trade_time = data.index[i]


# Check for tweezers 
# checks last two candles and if they are close enough in range
    tweezerBottoms = False
    tweezerTops = False
    
    prevprev_low = data["Low"].iloc[i-2]
    prev_low = data["Low"].iloc[i-1]

    prevprev_high = data["High"].iloc[i-2]
    prev_high = data["High"].iloc[i-1]

    if abs(prevprev_low - prev_low) / prevprev_low <= 0.01: #calculates the percentages
            tweezerBottoms = True 
    if abs(prevprev_high - prev_high) / prevprev_high <= 0.01:
            tweezerTops = True
    
    

    

    # Long signal
    if ((data["EMA_20"].iloc[i] > data["EMA_50"].iloc[i]) and tweezerBottoms):
        

        if cash > 0:
            long = True
            shares = cash / price
            price_entry_long = shares * price
            cash = 0  # all cash invested for now
            hourBought = trade_time
            display_time = str(trade_time)[:16]
            
            
            print(f"BUY at {price:.2f} | Shares: {shares:.4f} |Executed At:" + (display_time))
            
    
    # Exit buy position
    elif long and data["EMA_20"].iloc[i] < data["EMA_50"].iloc[i] and shares > 0:
        if (trade_time - hourBought) >= timedelta(hours=1):
            price_exit_long = shares * price
            profitOrLoss = price_exit_long - price_entry_long
            cash = cash + price_exit_long
            shares = 0
            


            display_time = str(trade_time)[:16]
            long = False
            print("SELL at " + str(round(price, 2)) + " |Executed At: " +(display_time))
            

            if (profitOrLoss <= 0):
                print(Fore.RED + "LOSS: " + str(round(profitOrLoss, 2)))
                print(Style.RESET_ALL )
            else: 
                print (Fore.GREEN + ("PROFIT: " + str(round(profitOrLoss, 2))))
                print(Style.RESET_ALL)
            
            
            
            print("Current Value: " + str(round(cash, 2)))
            
            print("__________")

    # Short signal
    elif ((data["EMA_20"].iloc[i] < data["EMA_50"].iloc[i]) and tweezerTops):
        if cash > 0:
            short = True
            shares = cash / price
            price_entry_short = shares * price
            cash = 0  
            hourBought = trade_time
            display_time = str(trade_time)[:16]
            
            
            print(f"SHORT at {price:.2f} | Shares: {shares:.4f} |Executed At:" + (display_time))

    # Exit short position
    elif short and data["EMA_20"].iloc[i] > data["EMA_50"].iloc[i] and shares > 0:
        if (trade_time - hourBought) >= timedelta(hours=1):   #hold it for at least 1 hour
            price_exit_short = price * shares
            profitOrLoss = (price_entry_short - price_exit_short) 
            cash += price_exit_short
            shares = 0
            
            


            display_time = str(trade_time)[:16]
            short = False
            print("BOUGHT at " + str(round(price, 2)) + " |Executed At: " + (display_time))

            if (profitOrLoss <= 0):
                print(Fore.RED + "LOSS: " + str(round(profitOrLoss, 2)))
                print(Style.RESET_ALL )
            else: 
                print (Fore.GREEN  + ("PROFIT: " + str(round(profitOrLoss, 2))))
                print(Style.RESET_ALL)


            print("Current Value: " + str(round(cash, 2)))
            print("__________")




final_value = cash + shares * data["Close"].iloc[-1]

print("\nFinal Portfolio Value: " + str(round(final_value, 2)))






##things that we can alter ##

# the range of for tweezers (depednding on the stock)
# the time that we are required to hold the stock - note currently BTC-USD holding for 1 hour is bringing in more profits


## still need to implement ##

# take into account volume, in low volume times buy half
#instead of tips we can also check the highest close + open from each 
# add onto winning trades and lessen losing trades
