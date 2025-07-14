import os
import time
import schedule
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# === User inputs: change these as needed ===
BASE_AUTOMATION_PROFILE_PATH = r"C:\Users\DELL 5550\Documents\AutomationProfile"  # custom folder to store Chrome profiles
PROFILE_NAMES = ["Default", "Profile1", "Profile2", "Profile3", "Profile4", "Profile5"]  # add or remove profile names
TARGETS = [
    "MUCHACHOAERIALS.COM",
    "Coach Jerryminds millionaires club 3.4",
    "Coach Jerryminds millionaires club 3.2",
    "Coach Jerryminds millionaires club 3.3",
    "Private Millionaires Training 3.1",
    "Private Millionaires Training 3.0",    
    # "Work Chat",
    # "Friends",
]
MESSAGE_TO_SEND = "You don't want to miss this \
By tomorrow morning, I'll be sharing here with you \"how you can go from making your first $500 in the next 30 days  \
to making at least a thousand dollars monthly using your smartphone\". Anticipate!!!"

# === Helper functions ===

def ensure_base_folder():
    if not os.path.exists(BASE_AUTOMATION_PROFILE_PATH):
        os.makedirs(BASE_AUTOMATION_PROFILE_PATH)
        print(f"Created base profile folder: {BASE_AUTOMATION_PROFILE_PATH}")

def create_profiles_and_login(profile_names):
    ensure_base_folder()
    for profile in profile_names:
        profile_path = os.path.join(BASE_AUTOMATION_PROFILE_PATH, profile)
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)
            print(f"Created profile folder: {profile_path}")

        print(f"\nOpening Chrome with profile '{profile}' for WhatsApp login...")
        options = Options()
        options.add_argument(f"--user-data-dir={BASE_AUTOMATION_PROFILE_PATH}")
        options.add_argument(f"--profile-directory={profile}")
        # Fix for Chrome startup issues:
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.get("https://web.whatsapp.com")
            print(f"Please scan the QR code for profile '{profile}'. Waiting 60 seconds...")
            time.sleep(60)  # Time to scan QR code and login
        except Exception as e:
            print(f"Error opening WhatsApp Web for profile '{profile}': {e}")
        finally:
            if driver:
                driver.quit()

def send_message_to_target(driver, target_name, message):
    try:
        search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
        search_box.click()
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.BACK_SPACE)
        time.sleep(1)

        search_box.send_keys(target_name)
        time.sleep(5)  # Wait for search results

        try:
            # Try to find the chat in the search result before pressing ENTER
            result_xpath = f'//span[@title="{target_name}"]'
            chat = driver.find_element(By.XPATH, result_xpath)
            chat.click()
            time.sleep(5)

            input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
            input_box.click()
            input_box.send_keys(message)
            input_box.send_keys(Keys.ENTER)
            print(f"Message sent to '{target_name}'")
            return True

        except NoSuchElementException:
            print(f"Target '{target_name}' not found. Skipping.")
            search_box.send_keys(Keys.ESCAPE)
            return False

    except NoSuchElementException:
        print(f"UI element not found for '{target_name}'")
        return False

def process_profile(profile, already_messaged):
    print(f"Processing profile: {profile}")
    options = Options()
    options.add_argument(f"--user-data-dir={BASE_AUTOMATION_PROFILE_PATH}")
    options.add_argument(f"--profile-directory={profile}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://web.whatsapp.com")
        print(f"Waiting for WhatsApp Web to load (20 seconds) for profile '{profile}'...")
        time.sleep(20)  # Wait for WhatsApp Web to be ready

        for target in TARGETS:
            if target in already_messaged:
                print(f"Skipping '{target}', already messaged.")
                continue
            sent = send_message_to_target(driver, target, MESSAGE_TO_SEND)
            if sent:
                already_messaged.add(target)
            time.sleep(3)

    except WebDriverException as e:
        print(f"WebDriver error for profile '{profile}': {e}")

    finally:
        if driver:
            driver.quit()
        print(f"Closed Chrome for profile '{profile}'")

def job():
    print("Starting scheduled message sending job...")
    profiles = PROFILE_NAMES
    print(f"Profiles to process: {profiles}")

    already_messaged = set()
    for profile in profiles:
        process_profile(profile, already_messaged)
        time.sleep(5)
    print("Scheduled job completed.\n")

def main():
    parser = argparse.ArgumentParser(description="WhatsApp Web Scheduler")
    parser.add_argument('--setup-profiles', action='store_true', help="Create Chrome profiles and open WhatsApp Web for QR code login")
    parser.add_argument('--run-scheduler', action='store_true', help="Run scheduled WhatsApp message sender")

    args = parser.parse_args()

    if args.setup_profiles:
        print("Starting profile setup and QR login process...")
        create_profiles_and_login(PROFILE_NAMES)
        print("Profile setup completed. You can now run the scheduler with --run-scheduler.")
    elif args.run_scheduler:
        print("Starting WhatsApp message scheduler...")
        schedule.every().day.at("19:59").do(job)  # change to your preferred schedule time

        print("Scheduler running. Press Ctrl+C to exit.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("Scheduler stopped by user.")
    else:
        print("No argument given. Use --setup-profiles to login or --run-scheduler to start scheduling.")

if __name__ == "__main__":
    main()
