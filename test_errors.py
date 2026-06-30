# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "selenium",
#     "webdriver-manager",
# ]
# ///

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1200,900")
options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    print("Membuka http://localhost:8502")
    driver.get("http://localhost:8502")
    time.sleep(5)  # Tunggu Streamlit render
    
    for entry in driver.get_log('browser'):
        print(f"CONSOLE: {entry['level']} - {entry['message']}")
        
finally:
    driver.quit()
