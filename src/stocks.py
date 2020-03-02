import discord
import os
import time
import datetime
from calendar import monthrange
from selenium import webdriver
from PIL import Image
from finnhub import client as Finnhub # api docs: https://finnhub.io/docs/api
import requests
import matplotlib
import mplfinance
import pandas as pd

FINNHUB_API_TOKEN = os.environ.get('FINNHUB_API_TOKEN')
finnhub_client = Finnhub.Client(api_key=FINNHUB_API_TOKEN)

async def stock_price_today(ctx, ticker):
    # for indexes 'stocks' needs to be 'index'
    quote = finnhub_client.quote(symbol=ticker.upper())
    current_price = quote["c"]
    price_change = current_price - quote["pc"]
    decimal_format = '{:,.2f}'
    
    try: # try stock
        percent_change = ((current_price / quote["pc"])-1) * 100
    except: # invalid ticker entered --> quote["pc"] = 0  leading to / 0
        try: # try crypto binance
            current_price, price_change, percent_change = get_crypto_data(ticker, 'BINANCE')
        except:
            try: # try crypto coinbase
                current_price, price_change, percent_change = get_crypto_data(ticker, 'COINBASE')
            except:
                await ctx.send(embed=discord.Embed(description='Invalid Ticker!', color=discord.Color.dark_red()))
                return
        decimal_format = '{:,.5f}'
        
    color = discord.Color.green() # default is price increase
    sign = '+'
    if price_change < 0: # price decrease
        price_change *= -1 # get rid of '-' sign
        percent_change *= -1 # get rid of '-' sign
        color = discord.Color.red()
        sign = '-'
    ccp = decimal_format.format(current_price).rstrip('0').rstrip('.') # cleaner current price format decimals and remove trailing 0s and .'s
    cpc = decimal_format.format(price_change).rstrip('0').rstrip('.') # cleaner price change format decimals and remove trailing 0s and .'s
    embedded_message = discord.Embed(
        # format with appropriate ','
        description=ticker.upper() + " Price: $" + ccp + " USD\nPrice Change: " + sign + "$" + cpc + " (" + sign + '{:,.2f}'.format(percent_change) + "%)", 
        color=color
        )
    embedded_message.set_footer(text='As of ' + str(time.ctime(time.time())))
    await ctx.send(embed=embedded_message)

# returns crypto data given the specified ticker and exchange
def get_crypto_data(ticker, exchange):
    candle_crypto = finnhub_client.crypto_candle(symbol=exchange + ':' + ticker.upper(), resolution="D", count=200)
    current_price = candle_crypto["c"][-1]
    price_change = current_price - candle_crypto["o"][-1]
    percent_change = ((current_price / candle_crypto["o"][-1])-1) * 100
    return candle_crypto["c"][-1], current_price - candle_crypto["o"][-1], ((current_price / candle_crypto["o"][-1])-1) * 100

async def chart(ctx, ticker, timeframe, chart_type):
    timeframe = timeframe.lower()

    # get current date
    current_day = datetime.datetime.now()

    # pull company info from finnhub client
    company_info = finnhub_client.company_profile(symbol=ticker.upper())

    # get the ipo date for the specified ticker
    try:
        ipo_date = company_info['ipo'].split('-') # [year, month, day]
    except: # ticker doesn't exist
        await ctx.send(embed=discord.Embed(description='Invalid ticker', color=discord.Color.dark_red()))
        return

    # calculate the difference between today and the ipo date
    ipo_difference = datetime.date.today() - datetime.date(int(ipo_date[0]), int(ipo_date[1]), int(ipo_date[2]))

    # set max_days
    max_days = ipo_difference.days

    # set num days based on timeframe
    if timeframe == 'd':
        stock_candle = finnhub_client.stock_candle(symbol=ticker.upper(), resolution='1', count=200)
        await ctx.send(embed=discord.Embed(description='Intraday is currently not supported', color=discord.Color.dark_red()))
        return
    elif timeframe == '5d':
        num_days = 5 if 5 < max_days else max_days
    elif timeframe == 'm':
        num_days = 30 if 30 < max_days else max_days
    elif timeframe == '6m':
        num_days = 182 if 182 < max_days else max_days
    elif timeframe == 'y':
        num_days = 365 if 365 < max_days else max_days
    elif timeframe == 'ytd':
        ytd_difference = datetime.date.today() - datetime.date(current_day.year, 1, 1) 
        ytd = ytd_difference.days
        num_days = ytd if ytd < max_days else max_days
    elif timeframe == '5y':
        num_days = 1825 if 1825 < max_days else max_days
    elif timeframe == 'max':
        num_days = max_days
    else:
        await ctx.send(embed=discord.Embed(description='Invalid timeframe specified!', color=discord.Color.dark_red()))
        return
    
    # build either line or candle graph
    if chart_type == 'candle':
        filename = candlestick(ticker.upper(), num_days, timeframe)
    elif chart_type == 'line':
        filename = line(ticker.upper(), num_days, timeframe)
    
    # send file to the calling channel
    await ctx.send(file=discord.File(filename))

    #remove file from os
    os.remove(filename)

def candlestick(ticker, days, period):
    df, start_price, end_price = create_dataframe(ticker, days)

    # define kwargs
    kwargs = dict(type='candle', title = ticker.upper() + ', ' + period.upper(), ylabel='Share Price', volume = True, figratio=(10,8))

    # Create my own `marketcolors` to use with the `nightclouds` style:
    mc = mplfinance.make_marketcolors(up='#00ff00',down='#ed2121',inherit=True)

    # Create a new style based on `nightclouds` but with my own `marketcolors`:
    s  = mplfinance.make_mpf_style(base_mpf_style='nightclouds',marketcolors=mc)

    # Plot the candlestick chart and save to ticker-chart.png
    filename = ticker.upper() + '-candle.png'
    save = dict(fname=filename, dpi = 100, pad_inches=0.25)
    mplfinance.plot(df, **kwargs, style=s, savefig=save)

    return filename

def line(ticker, days, period):
    df, start_price, end_price = create_dataframe(ticker, days)

    # define kwargs
    kwargs = dict(type='line', title = ticker.upper() + ', ' + period.upper(), ylabel='Share Price', volume = True, figratio=(10,8))

    # Create my own `marketcolors` to use with the `nightclouds` style:
    mc = mplfinance.make_marketcolors(up='#00ff00',down='#ed2121', inherit=True)

    # Create a new style based on `nightclouds` but with my own `marketcolors`:
    s  = mplfinance.make_mpf_style(base_mpf_style = 'nightclouds',marketcolors = mc, facecolor='w', edgecolor='#ed2121' if start_price > end_price else '#00ff00', mavcolors=['#ed2121' if start_price > end_price else '#00ff00']) 

    # Plot the candlestick chart and save to ticker-chart.png
    filename = ticker.upper() + '-line.png'
    save = dict(fname=filename, dpi = 100, pad_inches=0.25)
    mplfinance.plot(df, **kwargs, style=s, savefig=save)

    return filename

def create_dataframe(ticker, days):
    # api docs for financialmodelingprep.com: https://financialmodelingprep.com/developer/docs/
    r = requests.get(f'https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?timeseries={days}')
    r = r.json()

    # reformat the stock date from [{date: 'x-x-x', open: x, high: x, etc}, {}, {}, ...] to {Date: ['x-x-x', 'x-x-x', ...], Open: [x, x, ...], ...}
    stockdata = r['historical']
    reformatted_stockdata = dict()
    reformatted_stockdata['Date'] = []
    reformatted_stockdata['Open'] = []
    reformatted_stockdata['High'] = []
    reformatted_stockdata['Low'] = []
    reformatted_stockdata['Close'] = []
    reformatted_stockdata['Volume'] = []
    for index in range(len(stockdata)-1, -1, -1):
        reformatted_stockdata['Date'].append(stockdata[index]['date'])
        reformatted_stockdata['Open'].append(stockdata[index]['open'])
        reformatted_stockdata['High'].append(stockdata[index]['high'])
        reformatted_stockdata['Low'].append(stockdata[index]['low'])
        reformatted_stockdata['Close'].append(stockdata[index]['close'])
        reformatted_stockdata['Volume'].append(stockdata[index]['volume'])

    # Convert to dataframe
    stockdata_df = pd.DataFrame.from_dict(reformatted_stockdata) 

    # Set date as the index
    stockdata_df.set_index('Date', inplace=True)

    # Convert date to correct format
    stockdata_df.index = pd.to_datetime(stockdata_df.index)

    return stockdata_df, reformatted_stockdata['Close'][0], reformatted_stockdata['Close'][-1]