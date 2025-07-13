import os
import time
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# ----------- CORE CODE ------------

# BASE_PROFILE_PATH = r"C:\Users\DELL 5550\AppData\Local\Google\Chrome\User Data"
BASE_PROFILE_PATH = r"C:\Users\DELL 5550\AppData\Local\Google\Chrome\AutomationProfile"


def get_all_profiles():
    profiles = []
    for entry in os.listdir(BASE_PROFILE_PATH):
        full_path = os.path.join(BASE_PROFILE_PATH, entry)
        # Only include 'Default' and folders starting with 'Profile'
        if os.path.isdir(full_path) and (entry == "Default" or entry.startswith("Profile")):
            profiles.append(entry)
    return profiles

def create_driver_for_profile(profile):
    options = Options()
    options.add_argument(f"--user-data-dir={BASE_PROFILE_PATH}")
    options.add_argument(f"--profile-directory={profile}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.get("https://web.whatsapp.com")
    print(f"[{profile}] WhatsApp Web loading, please scan QR if needed...")
    time.sleep(15)  # Wait time for QR scan and page load
    return driver

def send_message_to_target(driver, target_name, message):
    try:
        search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
        search_box.click()
        search_box.clear()
        search_box.send_keys(target_name)
        time.sleep(5)

        try:
            search_box.send_keys(Keys.ENTER)
            time.sleep(5)
        except Exception:
            print(f"Target '{target_name}' not found.")
            return False

        input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
        input_box.click()
        input_box.send_keys(message)
        input_box.send_keys(Keys.ENTER)
        print(f"Message sent to '{target_name}'")
        return True

    except NoSuchElementException:
        print(f"UI element not found for '{target_name}'")
        return False

def job(drivers, targets, message):
    print("Starting scheduled message sending job...")
    for profile, driver in drivers.items():
        print(f"Sending messages using profile: {profile}")
        for target in targets:
            send_message_to_target(driver, target, message)
            time.sleep(3)
    print("Job completed.\n")

if __name__ == "__main__":
    # ----------- USER INPUTS BELOW ------------

    targets = [
        "MUCHACHOAERIALS.COM",
        # Add more target group/contact names here
    ]

    message_to_send = "Hello! This is an automated message."

    schedule_time = "02:54"  # 24-hour format HH:MM for scheduled sending

    # -------------------------------------------

    profiles = get_all_profiles()
    print(f"Profiles found: {profiles}")

    drivers = {}
    for profile in profiles:
        try:
            driver = create_driver_for_profile(profile)
            drivers[profile] = driver
        except WebDriverException as e:
            print(f"Error launching Chrome for profile '{profile}': {e}")

    schedule.every().day.at(schedule_time).do(job, drivers=drivers, targets=targets, message=message_to_send)

    print("WhatsApp scheduler running.")
    while True:
        schedule.run_pending()
        time.sleep(1)