from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os


def create_browser(environment):
    if environment == 'web':
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_locations = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--start-maximized')
        return webdriver.Chrome(executable_path = os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    else: # environment == 'local'
        return webdriver.Chrome(ChromeDriverManager().install())