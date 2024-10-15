import os
import sys
from pathlib import Path
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the configuration
config_path = project_root / 'src' / 'config' / 'fantrax_config.py'
config_vars = {}
with open(config_path, 'r') as config_file:
    exec(config_file.read(), config_vars)

FANTRAX_USERNAME = config_vars['FANTRAX_USERNAME']
FANTRAX_PASSWORD = config_vars['FANTRAX_PASSWORD']
FANTRAX_LOGIN_URL = config_vars['FANTRAX_LOGIN_URL']

def login_with_selenium():
    driver = webdriver.Chrome()  # Make sure you have chromedriver installed and in PATH
    driver.get("https://www.fantrax.com/login")
    
    # Wait for username field and enter username
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    username_field.send_keys(FANTRAX_USERNAME)
    
    # Enter password
    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(FANTRAX_PASSWORD)
    
    # Submit form
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    submit_button.click()
    
    # Wait for login to complete (adjust the condition as needed)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "some-element-present-after-login"))
    )
    
    # Now you can use driver.get() to navigate to your target URL and driver.page_source to get the content

    # Don't forget to close the browser when done
    driver.quit()

def download_fantrax_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.fantrax.com/',
        'Content-Type': 'application/json',
    }

    session = requests.Session()
    session.headers.update(headers)

    # Step 1: Get the login page to retrieve any necessary tokens
    login_page_url = "https://www.fantrax.com/login"
    login_page_response = session.get(login_page_url)
    print(f"Login page response status code: {login_page_response.status_code}")

    # Parse the login page HTML
    soup = BeautifulSoup(login_page_response.text, 'html.parser')
    
    # Look for any hidden input fields that might contain tokens
    hidden_inputs = soup.find_all("input", type="hidden")
    form_data = {input.get('name'): input.get('value') for input in hidden_inputs}
    
    # Add username and password to the form data
    form_data['username'] = FANTRAX_USERNAME
    form_data['password'] = FANTRAX_PASSWORD

    # Step 2: Submit the login form
    login_url = "https://www.fantrax.com/login"
    login_response = session.post(login_url, data=form_data)
    print(f"Login response status code: {login_response.status_code}")
    print(f"Login response content: {login_response.text[:500]}")

    # Now attempt to get the data
    response = session.get(url)
    print(f"Data download response status code: {response.status_code}")

    if "WARNING_NOT_LOGGED_IN" not in response.text:
        print("Successfully retrieved data:")
        print(response.text[:500])  # Print first 500 characters of the response
    else:
        print("Login failed. Please check your credentials.")
        print("Response content:")
        print(response.text[:500])  # Print first 500 characters of the response

# The URL you provided
url = "https://www.fantrax.com/fxpa/downloadPlayerStats?leagueId=o3pkjyf4lw5qg3tt&pageNumber=1&view=STATS&positionOrGroup=BASKETBALL_PLAYER&seasonOrProjection=PROJECTION_0_41j_SEASON&timeframeTypeCode=PROJECTED_SEASON&transactionPeriod=1&miscDisplayType=1&sortType=SCORE&maxResultsPerPage=20&statusOrTeamFilter=ALL_AVAILABLE&scoringCategoryType=7&timeStartType=PERIOD_ONLY&schedulePageAdj=0&searchName=&datePlaying=ALL&startDate=2024-10-22&endDate=2024-10-14&teamId=9oj2rg09lw5qg3uc&"

# Call this function instead of the previous login attempt
login_with_selenium()

download_fantrax_data(url)
