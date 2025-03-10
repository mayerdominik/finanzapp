import yfinance as yf
import pandas as pd

# Fetch the price of Core MSCI World USD (Acc) from LSE in USD
ticker = yf.Ticker("IWDA.L")
ticker = yf.Ticker("TGT")
data = ticker.history(period="1y", interval="1d")

print(data)

# Fetch the USD to EUR exchange rate
fx_rate = yf.Ticker("USDEUR=X")
fx_data = fx_rate.history(period="1y", interval="1d")

print(fx_data)

dates1 = pd.to_datetime(data.index).date
dates2 = pd.to_datetime(fx_data.index).date
for date in dates2:
    if date not in dates1:
        print(date)

# Align the dates and convert to EUR
data['Close_EUR'] = data['Close'] * fx_data['Close']
print(data[['Close', 'Close_EUR']].head())  # Display both USD and EUR prices



def get_stock_data(ticker, period, interval):
    # Fetch the price of the stock from LSE in USD with conversion to EUR
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)

    fx_rate = yf.Ticker("USDEUR=X")
    fx_data = fx_rate.history(period=period, interval=interval)

    # print(fx_data)

    #transform Datetime column to middle european time
    data.index = data.index.tz_convert('Europe/Berlin')

    data['Close_EUR'] = data['Close'] * fx_data['Close']
    return data