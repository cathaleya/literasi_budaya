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
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    print("Membuka http://localhost:8502")
    driver.get("http://localhost:8502")
    time.sleep(5)  # Tunggu Streamlit render
    
    # Click "Edit Biodata" to bypass it? No, initial page is Biodata.
    # We need to simulate filling biodata to reach "baca_buku"
    # Actually, we can just edit app.py temporarily to start at "baca_buku" for testing.
    
    driver.save_screenshot("screenshot.png")
    print("Screenshot tersimpan.")
finally:
    driver.quit()
