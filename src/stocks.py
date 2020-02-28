import discord
import os
import time
from selenium import webdriver
from PIL import Image
import requests

FINNHUB_API_TOKEN = os.environ.get('FINNHUB_API_TOKEN')

async def stock_price_today(ctx, ticker):
    # for indexes 'stocks' needs to be 'index'
    response = requests.get('https://finnhub.io/api/v1/quote?symbol=' + ticker.upper() + '&token='+ FINNHUB_API_TOKEN).json()
    current_price = response["c"]
    price_change = current_price - response["pc"]
    decimal_format = '{:,.2f}'
    
    try: # try stock
        percent_change = ((current_price / response["pc"])-1) * 100
    except: # invalid ticker entered --> response["pc"] = 0  leading to / 0
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
    embedded_message = discord.Embed(
        # format with appropriate ','
        description=ticker.upper() + " Price: $" + decimal_format.format(current_price) + " USD\nPrice Change: " + sign + "$" + decimal_format.format(price_change) + " (" + sign + '{:,.2f}'.format(percent_change) + "%)", 
        color=color
        )
    embedded_message.set_footer(text='As of ' + str(time.ctime(time.time())))
    await ctx.send(embed=embedded_message)

# returns crypto data given the specified ticker and exchange
def get_crypto_data(ticker, exchange):
    response = requests.get('https://finnhub.io/api/v1/crypto/candle?symbol=' + exchange + ':' + ticker + '&resolution=D&count=1&token=' + FINNHUB_API_TOKEN).json()
    current_price = response["c"][-1]
    price_change = current_price - response["o"][-1]
    percent_change = ((current_price / response["o"][-1])-1) * 100
    return response["c"][-1], current_price - response["o"][-1], ((current_price / response["o"][-1])-1) * 100


async def stock_chart(ctx, driver, ticker, graph_type, period):
    
    if await check_if_valid_input(ctx, graph_type, period) == -1:
        return
    url = 'https://finviz.com/quote.ashx?t=' + ticker + '&ty=' + graph_type + '&ta=0&p=' + period + '&b=1' 
    async with ctx.channel.typing():
        # get screenshot
        print('time1: ' + str(time.ctime(time.time())))
        driver.get(url)
        driver.set_window_size(1920, 1080)
        print('time2: ' + str(time.ctime(time.time())))

        # if chart doesn't exist then its an invalid ticker
        try:
            chart_element = driver.find_element_by_id('chart0')
        except:
            await ctx.channel.send(embed=discord.Embed(description='Invalid ticker!', color=discord.Color.red()))
            return
        print('time3: ' + str(time.ctime(time.time())))

        location = chart_element.location
        size = chart_element.size
        
        driver.save_screenshot(ticker + '.png')
        print('time4: ' + str(time.ctime(time.time())))
        # crop screenshot
        stock_image = Image.open(ticker + '.png')
        x = location['x']
        y = location['y']
        width = x + size['width']
        height = y + size['height']
        cropped_image = stock_image.crop((int(x), int(y), int(width), int(height)))
        cropped_image.save(ticker + '-cropped.png')
        print('time5: ' + str(time.ctime(time.time())))
        await ctx.channel.send(file=discord.File(ticker + '-cropped.png'))

        os.remove(ticker + '.png')
        os.remove(ticker + '-cropped.png')
    
#checks if the input is valid
async def check_if_valid_input(ctx, graph_type, period):
    if graph_type not in ['l', 'c']:
        await ctx.channel.send(embed=discord.Embed(description='Invalid chart type! Must be **c** for candle or **l** for line.', color=discord.Color.red()))
        return -1
    elif period not in ['d', 'w', 'm']:
        await ctx.channel.send(embed=discord.Embed(description='Invalid period type! Must be **d** for day, **w** for week, or **m** for month.', color=discord.Color.red()))
        return -1
    return 0