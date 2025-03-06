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

service = Service()
options = webdriver.ChromeOptions()
options.binary_location = PATHS['chrome_path']
options.add_argument("--log-level=1")
DRIVER = webdriver.Chrome(service=service, options=options)
WAIT = WebDriverWait(DRIVER, 15)
