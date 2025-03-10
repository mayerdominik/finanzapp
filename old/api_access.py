import requests
import pandas as pd
import matplotlib.pyplot as plt

#https://www.alphavantage.co/documentation/

def get_json_from_api(symbol, function='TIME_SERIES_INTRADAY', interval='60min', outputsize='full',month='2009-01'):
    apikey = 'OESWG0ON2RK7SYQI'
    if function == 'TIME_SERIES_INTRADAY':
        url = 'https://www.alphavantage.co/query?function='+function+'&symbol='+symbol+'&interval='+interval+'&apikey='+apikey+'&month='+month+'&outputsize='+outputsize
    elif function == 'TIME_SERIES_DAILY':
        url = 'https://www.alphavantage.co/query?function='+function+'&symbol='+symbol+'&apikey='+apikey+'&outputsize='+outputsize
    else:
        print('Function not recognized')
        
        return None
    
    
    
    r = requests.get(url)
    data = r.json()
    if 'Information' in data.keys():
        print(data['Information'])
        return None
    return data

def get_df_from_json(symbol, function='TIME_SERIES_INTRADAY', interval='60min', outputsize='full',month='2009-01'):
    data = get_json_from_api(symbol, function, interval, outputsize,month)
    if data is None:
        print("Data not accessible, max API calls today (25) reached")
        return None
    df = pd.DataFrame(data[f'Time Series ({interval})']).T
    df.index = pd.to_datetime(df.index)
    df['4. close'] = df['4. close'].astype(float)
    df['1. open'] = df['1. open'].astype(float)
    df['2. high'] = df['2. high'].astype(float)
    df['3. low'] = df['3. low'].astype(float)
    df['5. volume'] = df['5. volume'].astype(float)
    meta_data = data['Meta Data']
    return meta_data, df

#example use of the function
symbol = 'SAP'
meta_data, df = get_df_from_json(symbol, function='TIME_SERIES_DAILY', interval='Daily', outputsize='full')

fig, ax  = plt.subplots()
ax.plot(df.index, df['4. close'])

plt.show()

symbol = 'SAP'
meta_data, df = get_df_from_json(symbol, function='TIME_SERIES_INTRADAY', interval='60min', outputsize='full',month='2009-01')

fig, ax  = plt.subplots()
ax.plot(df.index, df['4. close'])

#rotate x-axis labels
ax.tick_params(axis='x', rotation=45)

plt.show()

#TODO Save the data to a csv file to avoid making multiple API calls