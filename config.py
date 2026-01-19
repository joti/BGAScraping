import yaml

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

PRIVCONFIG_FILE = r'conf_priv.yml'
with open(PRIVCONFIG_FILE, 'r') as f:
    config = yaml.safe_load(f)
    BGA_LOGIN = config['bga_login']
    PATHS = config['paths']

PUBCONFIG_FILE = r'conf_pub.yml'
with open(PUBCONFIG_FILE, 'r') as f:
    config = yaml.safe_load(f)
    BGA_DATA = config['bga_data']

output_dir = PATHS['output_dir']
input_dir = PATHS['input_dir']
db_path = PATHS['db_path']

def create_driver( headless = False, 
                   no_sandbox = False ):
    service = Service()
    options = webdriver.ChromeOptions()
    options.binary_location = PATHS['chrome_path']
    options.add_argument("--log-level=1")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    if no_sandbox:    
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 15)

    return driver, wait
