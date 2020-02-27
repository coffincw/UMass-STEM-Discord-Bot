import discord
import os
import time
from selenium import webdriver
from PIL import Image

async def stock_info(ctx):
    stock_ticker = ctx.message.content[7:].lower().strip()

    url = 'https://finance.yahoo.com/quote/' + stock_ticker
    async with ctx.channel.typing():
        # get screenshot
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_locations = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--start-maximized')
        driver = webdriver.Chrome(executable_path = os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
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