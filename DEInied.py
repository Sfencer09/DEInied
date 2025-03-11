import time
import os
import random
import argparse
from rich.console import Console
from seleniumwire.undetected_chromedriver.v2 import Chrome, ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import urlparse
from faker import Faker

console = Console()
log_debug = "[#6c757d]"
log_success = "[#06d6a0]"

fake = Faker()

def generate_random_email():
    first = fake.first_name().lower()
    last = fake.last_name().lower()
    return f"{first}.{last}@gmail.com"

def generate_random_location():
    try:
        county = fake.county()
    except AttributeError:
        county = fake.city()
    suffix = random.choice(["Unified School District", "School District", "County School District"])
    return f"{county} {suffix}"

def generate_random_description():
    target_length = random.randint(150, 400)
    words = []
    while len(" ".join(words)) < target_length:
        words.extend(fake.words(nb=random.randint(5, 15)))
    description = " ".join(words)
    if len(description) > target_length:
        description = description[:target_length].strip()
    return description

class MyScraper:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.driver = self.build_driver()

    def build_driver(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--user-data-dir=./user_profile')
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_prefs = {'excludeSwitches': ['disable-component-update']}
        capabilities = DesiredCapabilities.CHROME.copy()
        capabilities['goog:chromeOptions'] = chrome_prefs

        seleniumwire_options = {
            'disable_encoding': True,
            'verify_ssl': False  # Disable SSL certificate verification
        }
        if self.proxy:
            seleniumwire_options['proxy'] = {
                'https': self.proxy,
            }
            console.log(f"{log_debug}Using proxy: {self.proxy}")

        driver = Chrome(options=chrome_options, desired_capabilities=capabilities,
                        seleniumwire_options=seleniumwire_options, headless=False)
        driver.request_interceptor = self.intercept_request
        driver.response_interceptor = self.intercept_response
        return driver

    def intercept_request(self, request):
        parsed_url = urlparse(request.url)
        console.log(f"{log_debug}Browser is fetching... {request.url}[/]")

    def intercept_response(self, request, response):
        console.log(f"{log_success}Received response for: {request.url}[/]")

def fill_form(driver, file_attachment):
    try:
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        random_email = generate_random_email()
        email_input.clear()
        email_input.send_keys(random_email)
        console.log(f"{log_success}Email input filled with {random_email}!")
    except Exception as e:
        console.log(f"[bold red][!][/] Failed to fill email input: {e}")
        console.log(f"{log_debug}Email input not found. Reloading the page to reset state.")
        driver.get("https://enddei.ed.gov/")
        return False  # Indicate failure so the main loop can skip further processing

    try:
        location_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "location"))
        )
        random_location = generate_random_location()
        location_input.clear()
        location_input.send_keys(random_location)
        console.log(f"{log_success}Location input filled with {random_location}!")
    except Exception as e:
        console.log(f"[bold red][!][/] Failed to fill location input: {e}")

    try:
        zipcode_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "zipcode"))
        )
        random_zipcode = fake.zipcode()
        zipcode_input.clear()
        zipcode_input.send_keys(random_zipcode)
        console.log(f"{log_success}Zipcode input filled with {random_zipcode}!")
    except Exception as e:
        console.log(f"[bold red][!][/] Failed to fill zipcode input: {e}")

    try:
        description_textarea = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "description"))
        )
        random_description = generate_random_description()
        description_textarea.clear()
        description_textarea.send_keys(random_description)
        console.log(f"{log_success}Description filled with {len(random_description)} characters!")
    except Exception as e:
        console.log(f"[bold red][!][/] Failed to fill description textarea: {e}")

    try:
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "file"))
        )
        file_to_upload = os.path.abspath(file_attachment)
        file_input.send_keys(file_to_upload)
        console.log(f"{log_success}File input set with file: {file_to_upload}")
    except Exception as e:
        console.log(f"[bold red][!][/] Failed to upload file: {e}")

    return True  # Indicate success


def click_submit(driver):
    try:
        pause_time = random.uniform(2, 6)
        console.log(f"{log_debug}Pausing for {pause_time:.2f} seconds before clicking submit...[/]")
        time.sleep(pause_time)
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submitButton"))
        )
        actions = ActionChains(driver)
        actions.move_to_element(submit_button).pause(1).click().perform()
        console.log(f"{log_success}Submit button clicked!")
    except Exception as e:
        console.log(f"[bold red][!][/] Failed to click submit button: {e}")

def main(file_attachment, proxy):
    original_url = "https://enddei.ed.gov/"
    scraper = MyScraper(proxy=proxy)
    driver = scraper.driver

    driver.get(original_url)

    while True:
        fill_form(driver, file_attachment)
        click_submit(driver)
        time.sleep(5)
        current_url = driver.current_url
        console.log(f"{log_debug}Current URL after submission: {current_url}")

        while "/error" in current_url:
            console.log(f"[bold red]Submission error detected. Retrying...[/]")
            driver.back()
            retry_pause = random.uniform(2, 6)
            console.log(f"{log_debug}Pausing for {retry_pause:.2f} seconds before retrying submit...[/]")
            time.sleep(retry_pause)
            click_submit(driver)
            time.sleep(5)
            current_url = driver.current_url
            console.log(f"{log_debug}Current URL after retry: {current_url}")

        if "/thankyou" in current_url:
            console.log(f"{log_success}Submission successful! Navigating back to form.")
            driver.get(original_url)
            time.sleep(2)
        else:
            console.log(f"{log_debug}No definitive navigation detected. Refreshing form.")
            driver.get(original_url)
            time.sleep(2)
        del driver.requests # Clear temp storage

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--file-attachment", required=True, help="Path to the file to upload")
    parser.add_argument("--proxy", help="Proxy URL (e.g., socks5://user:pass@proxy:port)")
    args = parser.parse_args()
    main(args.file_attachment, args.proxy)
