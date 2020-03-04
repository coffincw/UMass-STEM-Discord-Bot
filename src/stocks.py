import discord
import os
import time
import datetime
from calendar import monthrange
from selenium import webdriver
from PIL import Image, ImageFont, ImageDraw
from finnhub import client as Finnhub # api docs: https://finnhub.io/docs/api
import requests
import matplotlib
import mplfinance
import pandas as pd

FINNHUB_API_TOKEN = os.environ.get('FINNHUB_API_TOKEN')
finnhub_client = Finnhub.Client(api_key=FINNHUB_API_TOKEN)

# helper function to get the +/- sign of the price and percent change
def get_string_change(current_price, price_change, percent_change, decimal_format):
    sign = '+'
    color = discord.Color.green()
    if price_change < 0: # price decrease
        price_change *= -1 # get rid of '-' sign
        percent_change *= -1 # get rid of '-' sign
        color = discord.Color.red()
        sign = '-'

    ccp = '$' + decimal_format.format(current_price).rstrip('0').rstrip('.') # cleaner current price format decimals and remove trailing 0s and .'s
    cpc = sign + "$" + decimal_format.format(price_change).rstrip('0').rstrip('.') # cleaner price change format decimals and remove trailing 0s and .'s
    cpercentc = sign + '{:,.2f}'.format(percent_change) + '%'
    return ccp, cpc, cpercentc, color


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
        
    ccp, cpc, cpercentc, color = get_string_change(current_price, price_change, percent_change, decimal_format)

    
    embedded_message = discord.Embed(
        # format with appropriate ','
        description=ticker.upper() + " Price: " + ccp + " USD\nPrice Change: " + cpc + " (" + cpercentc + ")", 
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

async def chart(ctx, ticker, timeframe, chart_type, path_addition):
    timeframe = timeframe.upper()
    ticker = ticker.upper()
    quote = requests.get(f'https://financialmodelingprep.com/api/v3/quote/{ticker}').json()
    current_price = quote[0]["price"]
    

    # get current date
    current_day = datetime.datetime.now()

    # pull company info from finnhub client
    company_info = finnhub_client.company_profile(symbol=ticker)

    # get the ipo date for the specified ticker
    try:
        ipo_date = company_info['ipo'].split('-') # [year, month, day]
        company_name = company_info['name']
    except: # ticker doesn't exist
        await ctx.send(embed=discord.Embed(description='Invalid ticker', color=discord.Color.dark_red()))
        return

    # calculate the difference between today and the ipo date
    ipo_difference = datetime.date.today() - datetime.date(int(ipo_date[0]), int(ipo_date[1]), int(ipo_date[2]))

    # set max_days
    max_days = ipo_difference.days

    # set num days based on timeframe
    if timeframe == 'D':
        num_days = 1
    elif timeframe == '5D':
        num_days = 5 if 5 < max_days else max_days
    elif timeframe == 'M':
        num_days = 22 if 22 < max_days else max_days
    elif timeframe == '6M':
        num_days = 130 if 130 < max_days else max_days
    elif timeframe == 'Y':
        num_days = 261 if 261 < max_days else max_days
    elif timeframe == 'YTD':
        ytd_difference = datetime.date.today() - datetime.date(current_day.year, 1, 1) 
        weeks = ytd_difference.days//7
        num_days = weeks*5 if weeks*5 < max_days else max_days
    elif timeframe == '5Y':
        num_days = 1305 if 1305 < max_days else max_days
    elif timeframe == 'MAX':
        num_days = max_days
    else:
        await ctx.send(embed=discord.Embed(description='Invalid timeframe specified!', color=discord.Color.dark_red()))
        return
    
    # build either line or candle graph
    if chart_type == 'candle':
        filename, start_price = candlestick(ticker, num_days, timeframe)
    elif chart_type == 'line':
        filename, start_price = line(ticker, num_days, timeframe, current_price)
    
    crop_chart(filename, path_addition, company_name + ', ' + timeframe, ticker + ', ' + timeframe, start_price, current_price, ) 

    # send file to the calling channel
    await ctx.send(file=discord.File(filename))

    #remove file from os
    os.remove(filename)

def crop_chart(filename, path_addition, title, alt_title, start_price, current_price):
    im = Image.open(filename)
    font = ImageFont.truetype(path_addition + 'fonts/timesbd.ttf', size=30)
    price_change = current_price - start_price
    percent_change = ((current_price / start_price)-1) * 100
    ccp, cpc, cpercentc, color = get_string_change(current_price, price_change, percent_change, '{:,.2f}')

    color = '#00ff00' if color == discord.Color.green() else '#ed2121'

    # get image width and height
    width, height = im.size

    left = 50
    top = 50
    right = width - 130
    bottom = height - 55

    # crop
    im = im.crop((left, top, right, bottom))

    draw = ImageDraw.Draw(im)

    # get new width and height
    width, height = im.size 
    title_width, title_height = draw.textsize(title, font=font)

    # if company name too long then use ticker
    if title_width > 400:
        title = alt_title
        title_width, title_height = draw.textsize(title, font=font)

    location = ((width-title_width)/2, 10)

    # draw title (Company Name, timeframe)
    draw.text(location, title ,fill='white',font=font) 

    # draw current price
    draw.text((100, 10), ccp, fill='#3ec2fa', font=font)

    # Use smaller font size
    font = ImageFont.truetype(path_addition + 'fonts/timesbd.ttf', size=20)

    # price change and percent change
    pcpc = cpc + ' (' + cpercentc + ')'

    # get price change and percent change width and height
    pc_width, pc_height = draw.textsize(pcpc, font=font)

    #draw price change and percent change
    draw.text((width-17-pc_width, 20), cpc + ' (' + cpercentc + ')', fill=color, font=font)

    im.save(filename)

def create_close_line(dates, close):
    data = dict()
    data['Date'] = dates
    data['Close'] = [close]
    for i in range(len(dates)-1):
        data['Close'].append(close)

    # Create the dataframe from dictionary
    previous_close = pd.DataFrame.from_dict(data)

    # Set date as the index
    previous_close.set_index('Date', inplace=True)

    # Convert date to correct format
    previous_close.index = pd.to_datetime(previous_close.index)
    return previous_close

def candlestick(ticker, days, period):
    df, start_price, dates = create_dataframe(ticker, days, 5)

    # define kwargs
    kwargs = dict(type='candle', ylabel='Share Price', volume = True, figratio=(10,8))

    # Create my own `marketcolors` to use with the `nightclouds` style:
    mc = mplfinance.make_marketcolors(up='#00ff00',down='#ed2121',inherit=True)

    # Add 'previous close' horizontal line
    previous_close_line = create_close_line(dates, start_price)
    guide_lines = mplfinance.make_addplot(previous_close_line, color='#3ec2fa', linestyle='dashdot')

    # Create a new style based on `nightclouds` but with my own `marketcolors`:
    s  = mplfinance.make_mpf_style(base_mpf_style='nightclouds',marketcolors=mc)

    # Plot the candlestick chart and save to ticker-chart.png
    filename = ticker.upper() + '-candle.png'
    save = dict(fname=filename, dpi = 100, pad_inches=0.25)
    mplfinance.plot(df, addplot=guide_lines, **kwargs, style=s, savefig=save)

    return filename, start_price

def line(ticker, days, period, current_price):
    df, start_price, dates = create_dataframe(ticker, days, 1)

    # define kwargs
    kwargs = dict(type='line', ylabel='Share Price', volume = True, figratio=(10,8))

    # Create my own `marketcolors` to use with the `nightclouds` style:
    mc = mplfinance.make_marketcolors(up='#00ff00',down='#ed2121', inherit=True)

    # Add 'previous close' horizontal line
    previous_close_line = create_close_line(dates, start_price)
    guide_lines = mplfinance.make_addplot(previous_close_line, color='#3ec2fa', linestyle='dashdot')

    # Create a new style based on `nightclouds` but with my own `marketcolors`:
    s  = mplfinance.make_mpf_style(base_mpf_style = 'nightclouds',marketcolors = mc, facecolor='w', edgecolor='#ed2121' if start_price > current_price else '#00ff00', mavcolors=['#ed2121' if start_price > current_price else '#00ff00']) 

    # Plot the candlestick chart and save to ticker-chart.png
    filename = ticker.upper() + '-line.png'
    save = dict(fname=filename, dpi = 100, pad_inches=0.25)
    mplfinance.plot(df, addplot=guide_lines, **kwargs, style=s, savefig=save)

    return filename, start_price

def create_dataframe(ticker, days, intraday_request_frequency):
    # api docs for financialmodelingprep.com: https://financialmodelingprep.com/developer/docs/
    intraday = False
    if days == 1: # intraday
        intraday = True
        stockdata = requests.get(f'https://financialmodelingprep.com/api/v3/historical-chart/{intraday_request_frequency}min/{ticker}').json()
        
        # most recent trading day info
        time_format = '%Y-%m-%d %H:%M:%S'
        last_trading_day = datetime.datetime.strptime(stockdata[0]['date'], time_format).date() 
    else:
        stockdata = requests.get(f'https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?timeseries={days}').json()
        stockdata = stockdata['historical']

    # reformat the stock date from [{date: 'x-x-x', open: x, high: x, etc}, {}, {}, ...] to {Date: ['x-x-x', 'x-x-x', ...], Open: [x, x, ...], ...}
    reformatted_stockdata = dict()
    reformatted_stockdata['Date'] = []
    reformatted_stockdata['Open'] = []
    reformatted_stockdata['High'] = []
    reformatted_stockdata['Low'] = []
    reformatted_stockdata['Close'] = []
    reformatted_stockdata['Volume'] = []
    for index in range(len(stockdata)-1, -1, -1):
        if not intraday or datetime.datetime.strptime(stockdata[index]['date'], time_format).date() == last_trading_day:
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

    return stockdata_df, reformatted_stockdata['Close'][0], reformatted_stockdata['Date']