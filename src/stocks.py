import discord
import os
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from PIL import Image

async def stock_info(ctx):
    stock_ticker = ctx.message.content[7:].lower().strip()

    url = 'https://finance.yahoo.com/quote/' + stock_ticker
    async with ctx.channel.typing():
        # get screenshot
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--start-maximized')
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options )
        driver.get(url)
        driver.set_window_size(1920, 1080)
        time.sleep(2)
        driver.save_screenshot(stock_ticker + '.png')
        driver.close()

        # crop screenshot
        stock_image = Image.open(stock_ticker + '.png')
        left = 330
        top = 260
        right = 1226
        bottom = 725
        cropped_image = stock_image.crop((left, top, right, bottom))
        cropped_image.save(stock_ticker + '-cropped.png')
        await ctx.channel.send(file=discord.File(stock_ticker + '-cropped.png'))

        os.remove(stock_ticker + '.png')
        os.remove(stock_ticker + '-cropped.png')