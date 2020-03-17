import discord
import os
import time
import re
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
    quote, decimal_format = get_quote(ticker.upper())
    if quote['t'] == 0:
        await ctx.send(embed=discord.Embed(description='Invalid Ticker!', color=discord.Color.dark_red()))
        return
    current_price = quote["c"]
    price_change = current_price - quote["pc"]
    percent_change = ((current_price / quote["pc"])-1) * 100
    
    ccp, cpc, cpercentc, color = get_string_change(current_price, price_change, percent_change, decimal_format)

    
    embedded_message = discord.Embed(
        # format with appropriate ','
        description=ticker.upper() + " Price: " + ccp + " USD\nPrice Change: " + cpc + " (" + cpercentc + ")", 
        color=color
        )
    embedded_message.set_footer(text='As of ' + str(time.ctime(time.time())))
    await ctx.send(embed=embedded_message)

def get_quote(ticker):
    quote = finnhub_client.quote(symbol=ticker)
    if quote['t'] != 0:
        return quote, '{:,.2f}'
    quote = finnhub_client.quote(symbol='BINANCE:' + ticker)
    if quote['t'] != 0:
        return quote, '{:,.5f}'
    quote = finnhub_client.quote(symbol='COINBASE:' + ticker)
    if quote['t'] != 0:
        return quote, '{:,.5f}'
    
    # Iterate through remaining exchanges
    crypto_exchanges = finnhub_client.crypto_exchange()
    for exchange in crypto_exchanges:
        quote = finnhub_client.quote(symbol=exchange + ':' + ticker)
        if quote['t'] != 0:
            return quote, '{:,.5f}'
    
    return quote, None

def get_crypto_candle_data(ticker, to_time, from_time, res):
    # """Gets the json for the crypto candle data for the ticker
    # If ticker doesn't exist then it will return a json block:
    # { s: 'no_data'}
    # """
    candle_crypto = finnhub_client.crypto_candle(symbol = 'BINANCE:'+ ticker, resolution=res, **{'from':str(from_time), 'to': str(to_time)})
    status = candle_crypto['s']
    if status == 'ok':
        return candle_crypto
    candle_crypto = finnhub_client.crypto_candle(symbol = 'COINBASE:'+ ticker, resolution=res, **{'from':str(from_time), 'to': str(to_time)})
    status = candle_crypto['s']
    if status == 'ok':
        return candle_crypto
    
    # Iterate through remaining exchanges
    crypto_exchanges = finnhub_client.crypto_exchange()
    for exchange in crypto_exchanges:
        candle_crypto = finnhub_client.crypto_candle(symbol = exchange + ':'+ ticker, resolution=res, **{'from':str(from_time), 'to': str(to_time)})
        status = candle_crypto['s']
        if status == 'ok':
            return candle_crypto 
    # status is never 'ok' returns { s: 'no_data'}
    return candle_crypto 
    
def get_num_days(timeframe):
    d = re.compile('\d+[D]')
    m = re.compile('\d+[M]')
    w = re.compile('\d+[W]')
    y = re.compile('\d+[Y]')


    # set num days based on timeframe
    if timeframe == 'D' or d.match(timeframe) is not None:
        timeframe = timeframe[:-1] # trim off 'D'
        if len(timeframe) == 0: # was just 'D'
            num_days = 1
        else:
            num_days = int(timeframe)
    elif timeframe == 'W' or w.match(timeframe) is not None:
        timeframe = timeframe[:-1] # trim off 'M'
        if len(timeframe) == 0: # was just 'M'
            num_days = 7
        else:
            num_days = int(timeframe) * 7
    elif timeframe == 'M' or m.match(timeframe) is not None:
        timeframe = timeframe[:-1] # trim off 'M'
        if len(timeframe) == 0: # was just 'M'
            num_days = 30
        else:
            num_days = int(timeframe) * 30
    elif timeframe == 'Y' or y.match(timeframe) is not None:
        timeframe = timeframe[:-1] # trim off 'Y'
        if len(timeframe) == 0: # was just 'Y'
            num_days = 365
        else:
            num_days = int(timeframe) * 365
    elif timeframe == 'MAX':
        num_days = 15000
    else:
        num_days = -1
    return num_days

async def chart(ctx, ticker, timeframe, chart_type, path_addition):
    timeframe = timeframe.upper()
    ticker = ticker.upper()
    quote, dec = get_quote(ticker)
    current_price = quote['c']

    # get current date
    current_day = datetime.datetime.now()

    # pull company info from finnhub client
    company_info = finnhub_client.company_profile(symbol=ticker)

    # get the ipo date for the specified ticker
    try:
        ipo_date = company_info['ipo'].split('-') # [year, month, day]
        company_name = company_info['name']
    except: # ticker doesn't exist
        company_name = ticker

    # # calculate the difference between today and the ipo date
    # ipo_difference = datetime.date.today() - datetime.date(int(ipo_date[0]), int(ipo_date[1]), int(ipo_date[2]))

    num_days = get_num_days(timeframe)
    if num_days == -1:
        await ctx.send(embed=discord.Embed(description='Invalid timeframe specified!', color=discord.Color.dark_red()))
        return
    
    # build either line or candle graph
    if chart_type == 'candle':
        filename, start_price = candlestick(ticker, num_days, timeframe, quote)
    elif chart_type == 'line':
        filename, start_price = line(ticker, num_days, timeframe, quote)
    
    if start_price == -1:
        await ctx.send(embed=discord.Embed(description='Invalid ticker', color=discord.Color.dark_red()))
        return

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

def create_endtrading_line(dates, low, high):
    today = datetime.datetime.now()
    date = datetime.datetime(today.year, today.month, today.day, 16)
    data = dict()
    data['Close'] = []
    data['Date'] = dates
    skip = False
    for i in range(len(dates)):
        if skip:
            skip = False
            continue
        if dates[i] == date:
            data['Close'].extend([0, 999999])
            skip = True
            continue
        data['Close'].append(float('nan'))
    # Create the dataframe from dictionary
    end_trading = pd.DataFrame.from_dict(data)

    # Set date as the index
    end_trading.set_index('Date', inplace=True)

    # Convert date to correct format
    end_trading.index = pd.to_datetime(end_trading.index)
    return end_trading


def candlestick(ticker, days, period, quote):
    df, dates, create_vert_line, start_price = create_dataframe(ticker, days, 5, quote['pc'])
    if quote['t'] == 0: #invalid ticker
        return '', -1
    # define kwargs
    kwargs = dict(type='candle', ylabel='Share Price', volume = True, figratio=(10,8))

    # Create my own `marketcolors` to use with the `nightclouds` style:
    mc = mplfinance.make_marketcolors(up='#00ff00',down='#ed2121',inherit=True)

    # Add 'previous close' horizontal line and 'end trading' verticle line
    previous_close_line = create_close_line(dates, start_price)
    guide_lines = [
        mplfinance.make_addplot(previous_close_line, color='#3ec2fa', linestyle='dashdot')
    ]
    
    
    today = datetime.datetime.now()
    closing = datetime.datetime(today.year, today.month, today.day, 16) # closing time object
    day_of_the_week = datetime.datetime.today().weekday()
    
    if create_vert_line and (today > closing or day_of_the_week > 4):
        low = quote['l'] if quote['l'] < start_price else start_price
        high = quote['h'] if quote['h'] > start_price else start_price
        endtrading_line = create_endtrading_line(dates, low, high)
        guide_lines.append(mplfinance.make_addplot(endtrading_line, color='#fcfc03'))
    
    # Create a new style based on `nightclouds` but with my own `marketcolors`:
    s  = mplfinance.make_mpf_style(base_mpf_style='nightclouds',marketcolors=mc)

    # Plot the candlestick chart and save to ticker-chart.png
    filename = ticker.upper() + '-candle.png'
    save = dict(fname=filename, dpi = 100, pad_inches=0.25)
    mplfinance.plot(df, addplot=guide_lines, **kwargs, style=s, savefig=save)

    return filename, quote['pc']

def line(ticker, days, period, quote):
    df, dates, create_vert_line, start_price = create_dataframe(ticker, days, 1, quote['pc'])
    
    if quote['t'] == 0: #invalid ticker
        return '', -1

    # define kwargs
    kwargs = dict(type='line', ylabel='Share Price', volume = True, figratio=(10,8))

    # Create my own `marketcolors` to use with the `nightclouds` style:
    mc = mplfinance.make_marketcolors(up='#00ff00',down='#ed2121', inherit=True)

    # Add 'previous close' horizontal line and 'end trading' verticle line
    previous_close_line = create_close_line(dates, start_price)
    guide_lines = [
        mplfinance.make_addplot(previous_close_line, color='#3ec2fa', linestyle='dashdot')
    ]
    
    
    today = datetime.datetime.now()
    closing = datetime.datetime(today.year, today.month, today.day, 16) # closing time object
    day_of_the_week = datetime.datetime.today().weekday()
    
    if create_vert_line and (today > closing or day_of_the_week > 4):
        low = quote['l'] if quote['l'] < start_price else start_price
        high = quote['h'] if quote['h'] > start_price else start_price
        endtrading_line = create_endtrading_line(dates, low, high)
        guide_lines.append(mplfinance.make_addplot(endtrading_line, color='#fcfc03'))

    # Create a new style based on `nightclouds` but with my own `marketcolors`:
    s  = mplfinance.make_mpf_style(base_mpf_style = 'nightclouds',marketcolors = mc) 

    # Plot the candlestick chart and save to ticker-chart.png
    filename = ticker.upper() + '-line.png'
    save = dict(fname=filename, dpi = 100, pad_inches=0.25)
    mplfinance.plot(df, addplot=guide_lines, **kwargs, linecolor='#ed2121' if start_price > quote['c'] else '#00ff00', style=s, savefig=save)

    return filename, start_price

def get_from_time(days):
    today = datetime.datetime.now()
    opening = datetime.datetime(today.year, today.month, today.day, 9, 30) # opening time object
    day_of_the_week = datetime.datetime.today().weekday()

    if days == 1:
        if day_of_the_week < 5 and today > opening: # weekday after trading starts
            from_time = int(opening.timestamp())
        elif day_of_the_week < 5: # weekday before trading time
            prevday = opening - datetime.timedelta(days=1)
            from_time = int(prevday.timestamp())
        else: # weekend
            prevday = opening - datetime.timedelta(days=(day_of_the_week-4))
            from_time = int(prevday.timestamp())
    else:
        days_ago = opening - datetime.timedelta(days=days+1)
        from_time = int(days_ago.timestamp())

    return from_time

def get_candle_data(ticker, res, days):
    from_time = get_from_time(days)
    current_time = int(datetime.datetime.now().timestamp())
    candle = finnhub_client.stock_candle(symbol=ticker, resolution=res, **{'from':str(from_time), 'to': str(current_time)})
    status = candle['s']
    is_not_crypto = True
    if status != 'ok':
        if days == 1:
            prev = today-datetime.timedelta(days=1)
            from_time = int(prev.timestamp())
        candle = get_crypto_candle_data(ticker, current_time, from_time, res)
        is_not_crypto = False
    
    return candle, is_not_crypto

def create_dataframe(ticker, days, res, previous_close):
    # api docs for financialmodelingprep.com: https://financialmodelingprep.com/developer/docs/
    if days == 1: # intraday
        stockdata, is_intraday_not_crypto = get_candle_data(ticker, res, days)
        status = stockdata['s']
        if status != 'ok': # invalid ticker
            return None, None, True, -1
    elif days < 6:
        if res == 5:
            res = 60
        else:
            res = 30
        stockdata, is_intraday_not_crypto = get_candle_data(ticker, res, days)
        status = stockdata['s']
        is_intraday_not_crypto = False # override function output
        if status != 'ok': # invalid ticker
            return None, None, False, -1
    else:
        stockdata, is_intraday_not_crypto = get_candle_data(ticker, 'D', days)
        status = stockdata['s']
        is_intraday_not_crypto = False # override function output
        if status != 'ok': # invalid ticker
            return None, None, False, -1

    # # reformat the stock date from [{date: 'x-x-x', open: x, high: x, etc}, {}, {}, ...] to {Date: ['x-x-x', 'x-x-x', ...], Open: [x, x, ...], ...}
    reformatted_stockdata = dict()
    
    reformatted_stockdata['Date'] = []
    reformatted_stockdata['Open'] = []
    reformatted_stockdata['High'] = []
    reformatted_stockdata['Low'] = []
    reformatted_stockdata['Close'] = []
    reformatted_stockdata['Volume'] = []
    if days == 1:
        reformatted_stockdata['Date'].append(datetime.datetime.fromtimestamp(stockdata['t'][0]) - datetime.timedelta(days=1))
        reformatted_stockdata['Open'].append(previous_close)
        reformatted_stockdata['High'].append(previous_close)
        reformatted_stockdata['Low'].append(previous_close)
        reformatted_stockdata['Close'].append(previous_close)
        reformatted_stockdata['Volume'].append(0)
    for index in range(len(stockdata['t'])):
        reformatted_stockdata['Date'].append(datetime.datetime.fromtimestamp(stockdata['t'][index]))
        reformatted_stockdata['Open'].append(stockdata['o'][index])
        reformatted_stockdata['High'].append(stockdata['h'][index])
        reformatted_stockdata['Low'].append(stockdata['l'][index])
        reformatted_stockdata['Close'].append(stockdata['c'][index])
        reformatted_stockdata['Volume'].append(stockdata['v'][index])

    # Convert to dataframe
    stockdata_df = pd.DataFrame.from_dict(reformatted_stockdata) 

    # Set date as the index
    stockdata_df.set_index('Date', inplace=True)

    # Convert date to correct format
    stockdata_df.index = pd.to_datetime(stockdata_df.index)

    return stockdata_df, reformatted_stockdata['Date'], is_intraday_not_crypto, reformatted_stockdata['Close'][0]