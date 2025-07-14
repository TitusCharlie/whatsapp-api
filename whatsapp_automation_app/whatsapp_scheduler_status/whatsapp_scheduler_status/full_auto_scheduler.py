# whatsapp_automation_app.py
import os
import time
import json
import threading
import schedule
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import chromedriver_autoinstaller

# === CONFIGURATION ===
BASE_AUTOMATION_PROFILE_PATH = r"C:\\Users\\DELL 5550\\Documents\\AutomationProfile"
PROFILE_NAMES = ["Default", "Profile1", "Profile2", "Profile3", "Profile4", "Profile5"]

TASKS_FILE = "tasks.json"

# === TASK MODEL ===
class Task:
    def __init__(self, task_type, message=None, media_path=None, caption=None,
                 targets=None, profiles=None, schedule_time=None, status="pending",
                 created_at=None, last_error=None, id=None, **kwargs):
        self.id = id or f"task_{int(time.time() * 1000)}"
        self.task_type = task_type
        self.message = message
        self.media_path = media_path
        self.caption = caption
        self.targets = targets or []
        self.profiles = profiles or []
        self.schedule_time = schedule_time
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.last_error = last_error

# class Task:
#     def __init__(self, task_type, message=None, media_path=None, caption=None,
#                  targets=None, profiles=None, schedule_time=None):
#         self.id = f"task_{int(time.time() * 1000)}"
#         self.task_type = task_type
#         self.message = message
#         self.media_path = media_path
#         self.caption = caption
#         self.targets = targets or []
#         self.profiles = profiles or []
#         self.schedule_time = schedule_time
#         self.status = "pending"
#         self.created_at = datetime.now().isoformat()
#         self.last_error = None

    def to_dict(self):
        return self.__dict__

# === TASK REPOSITORY ===
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r') as f:
        return [Task(**t) for t in json.load(f)]

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump([t.to_dict() for t in tasks], f, indent=2)

# === WHATSAPP AUTOMATION CORE ===
def ensure_base_folder():
    if not os.path.exists(BASE_AUTOMATION_PROFILE_PATH):
        os.makedirs(BASE_AUTOMATION_PROFILE_PATH)

def launch_driver(profile):
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument(f"--user-data-dir={BASE_AUTOMATION_PROFILE_PATH}")
    options.add_argument(f"--profile-directory={profile}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless=new")
    return webdriver.Chrome(options=options)

def send_message(driver, target_name, message):
    try:
        search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
        search_box.click()
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.BACK_SPACE)
        time.sleep(1)

        search_box.send_keys(target_name)
        time.sleep(5)

        result_xpath = f'//span[@title="{target_name}"]'
        chat = driver.find_element(By.XPATH, result_xpath)
        chat.click()
        time.sleep(3)

        input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
        input_box.click()
        input_box.send_keys(message)
        input_box.send_keys(Keys.ENTER)
        return True
    except Exception as e:
        print(f"Error messaging {target_name}: {e}")
        return False

def upload_status(driver, media_path, caption):
    try:
        status_button = driver.find_element(By.XPATH, '//div[@title="Status"]')
        status_button.click()
        time.sleep(2)

        attach_input = driver.find_element(By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
        attach_input.send_keys(media_path)
        time.sleep(5)

        if caption:
            caption_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="6"]')
            caption_box.send_keys(caption)
            time.sleep(1)

        send_button = driver.find_element(By.XPATH, '//span[@data-icon="send"]')
        send_button.click()
        return True
    except Exception as e:
        print(f"Error uploading status: {e}")
        return False

def send_media(driver, target_name, media_path, caption):
    try:
        search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
        search_box.click()
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.BACK_SPACE)
        time.sleep(1)

        search_box.send_keys(target_name)
        time.sleep(5)

        result_xpath = f'//span[@title="{target_name}"]'
        chat = driver.find_element(By.XPATH, result_xpath)
        chat.click()
        time.sleep(3)

        attach_button = driver.find_element(By.XPATH, '//div[@title="Attach"]')
        attach_button.click()
        time.sleep(1)

        media_input = driver.find_element(By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
        media_input.send_keys(media_path)
        time.sleep(3)

        if caption:
            caption_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
            caption_box.send_keys(caption)
            time.sleep(1)

        send_btn = driver.find_element(By.XPATH, '//span[@data-icon="send"]')
        send_btn.click()
        return True
    except Exception as e:
        print(f"Error sending media to {target_name}: {e}")
        return False

# === TASK EXECUTION ===
def run_task(task):
    task.status = "running"
    for profile in task.profiles:
        driver = None
        try:
            driver = launch_driver(profile)
            driver.get("https://web.whatsapp.com")
            time.sleep(20)

            if task.task_type == "message":
                for target in task.targets:
                    send_message(driver, target, task.message)
                    time.sleep(2)
            elif task.task_type == "status":
                upload_status(driver, task.media_path, task.caption)
            elif task.task_type == "media":
                for target in task.targets:
                    send_media(driver, target, task.media_path, task.caption)
                    time.sleep(2)

            task.status = "completed"
        except Exception as e:
            task.status = "failed"
            task.last_error = str(e)
        finally:
            if driver:
                driver.quit()

# === SCHEDULER THREAD ===
def task_scheduler():
    while True:
        tasks = load_tasks()
        now = datetime.now()
        for task in tasks:
            try:
                task_time = datetime.strptime(task.schedule_time, "%Y-%m-%d %H:%M")
                if task.status == "pending" and now >= task_time:
                    threading.Thread(target=run_task, args=(task,)).start()
            except Exception as e:
                print(f"Error parsing task time: {e}")
        save_tasks(tasks)
        time.sleep(60)

# === MAIN FUNCTION ===
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--add-task', choices=['message', 'media', 'status'], help='Create a task of type')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--setup-profiles', action='store_true')
    args = parser.parse_args()

    if args.setup_profiles:
        ensure_base_folder()
        for profile in PROFILE_NAMES:
            profile_path = os.path.join(BASE_AUTOMATION_PROFILE_PATH, profile)
            if not os.path.exists(profile_path):
                os.makedirs(profile_path)

            print(f"Opening Chrome for '{profile}' to login...")
            driver = launch_driver(profile)
            driver.get("https://web.whatsapp.com")
            print(f"Scan QR for profile '{profile}'...")
            time.sleep(60)
            driver.quit()

    elif args.add_task:
        task_type = args.add_task
        schedule_time = input("Enter schedule time (YYYY-MM-DD HH:MM): ")
        targets = input("Enter comma-separated target names (for message/media tasks): ").split(',')
        profiles = input("Enter comma-separated profile names: ").split(',')

        if task_type == "message":
            message = input("Enter message text: ")
            t = Task(
                task_type="message",
                message=message,
                targets=targets,
                profiles=profiles,
                schedule_time=schedule_time
            )
        elif task_type == "media":
            media_path = input("Enter full path to media file: ")
            caption = input("Enter caption (optional): ")
            t = Task(
                task_type="media",
                media_path=media_path,
                caption=caption,
                targets=targets,
                profiles=profiles,
                schedule_time=schedule_time
            )
        elif task_type == "status":
            media_path = input("Enter full path to status media file: ")
            caption = input("Enter caption (optional): ")
            t = Task(
                task_type="status",
                media_path=media_path,
                caption=caption,
                profiles=profiles,
                schedule_time=schedule_time
            )
        tasks = load_tasks()
        tasks.append(t)
        save_tasks(tasks)
        print(f"{task_type.capitalize()} task created and saved.")

    elif args.run:
        print("Starting task scheduler...")
        task_scheduler()

if __name__ == "__main__":
    main()