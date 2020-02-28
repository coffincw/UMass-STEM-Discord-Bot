import discord
import os
import time
from selenium import webdriver
from PIL import Image

# will not work while locally hosted due to chrome driver.  
async def stock_info(ctx, driver, ticker, graph_type, period):
    if await check_if_valid_input(ctx, graph_type, period) == -1:
        return
    url = 'https://finviz.com/quote.ashx?t=' + ticker + '&ty=' + graph_type + '&ta=0&p=' + period + '&b=1' 
    async with ctx.channel.typing():
        # get screenshot
        
        driver.get(url)
        driver.set_window_size(1920, 1080)

        # if chart doesn't exist then its an invalid ticker
        try:
            chart_element = driver.find_element_by_id('chart0')
        except:
            await ctx.channel.send(embed=discord.Embed(description='Invalid ticker!', color=discord.Color.red()))
            return

        location = chart_element.location
        size = chart_element.size
        
        driver.save_screenshot(ticker + '.png')

        # crop screenshot
        stock_image = Image.open(ticker + '.png')
        x = location['x']
        y = location['y']
        width = x + size['width']
        height = y + size['height']
        cropped_image = stock_image.crop((int(x), int(y), int(width), int(height)))
        cropped_image.save(ticker + '-cropped.png')
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