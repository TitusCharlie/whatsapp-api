import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException, 
                                      TimeoutException, 
                                      StaleElementReferenceException)
import chromedriver_autoinstaller

# Configuration
BASE_PROFILE_PATH = os.path.join(os.path.expanduser("~"), "Documents", "AutomationProfile")
TASKS_FILE = 'tasks.json'
MAX_RETRIES = 3
WAIT_TIMEOUT = 30

def launch_driver(profile_name):
    """Initialize Chrome driver with specified WhatsApp profile"""
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument(f"--user-data-dir={BASE_PROFILE_PATH}")
    options.add_argument(f"--profile-directory={profile_name}")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    return webdriver.Chrome(options=options)

def clear_text_field(element):
    """Clear text field reliably"""
    element.send_keys(Keys.CONTROL + "a")
    element.send_keys(Keys.BACKSPACE)
    time.sleep(0.5)

class Task:
    """Represents an automation task with proper null handling"""
    def __init__(self, task_type, content=None, message=None, content_type=None, 
                 targets=None, profiles=None, schedule_time=None, status="pending", 
                 caption=None, id=None, media_path=None, created_at=None, last_error=None):
        self.id = id or f"task_{int(time.time() * 1000)}"
        self.task_type = task_type
        self.content = content or message or ""
        self.content_type = content_type or ('media' if media_path else 'text')
        self.targets = targets if targets is not None else []
        self.profiles = profiles if profiles is not None else []
        self.schedule_time = schedule_time
        self.status = status
        self.caption = caption or ""
        self.created_at = created_at or datetime.now().isoformat()
        self.last_error = last_error or ""
        self.media_path = media_path or ""

    def to_dict(self):
        """Convert task to dictionary, omitting empty values"""
        task_dict = {
            'id': self.id,
            'task_type': self.task_type,
            'content': self.content,
            'content_type': self.content_type,
            'targets': self.targets,
            'profiles': self.profiles,
            'schedule_time': self.schedule_time,
            'status': self.status,
            'caption': self.caption,
            'created_at': self.created_at,
            'last_error': self.last_error,
            'media_path': self.media_path
        }
        # Remove empty strings and None values
        return {k: v for k, v in task_dict.items() if v not in [None, ""]}

def load_tasks():
    """Load tasks with proper null handling"""
    if not os.path.exists(TASKS_FILE):
        return []
    
    try:
        with open(TASKS_FILE, 'r') as f:
            tasks_data = json.load(f)
            return [Task(**{k: v or None for k, v in task_data.items()}) for task_data in tasks_data]
    except Exception as e:
        print(f"Error loading tasks: {str(e)}")
        return []

def save_tasks(tasks):
    """Save tasks with clean JSON output"""
    with open(TASKS_FILE, 'w') as f:
        json.dump([task.to_dict() for task in tasks], f, indent=2, ensure_ascii=False)

def safe_click(driver, xpath, timeout=WAIT_TIMEOUT):
    """Click element with retries and safety checks"""
    for _ in range(MAX_RETRIES):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            element.click()
            return True
        except Exception as e:
            print(f"Click failed (attempt {_+1}): {str(e)}")
            time.sleep(2)
    return False

def post_status(driver, content, content_type, caption=None):
    """Post to WhatsApp status with enhanced reliability"""
    try:
        if not safe_click(driver, '//div[@title="Status"]'):
            raise Exception("Could not click status tab")

        time.sleep(3)
        
        if content_type == "media":
            if not os.path.exists(content):
                raise FileNotFoundError(f"Media not found: {content}")
            
            media_input = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/*"]'))
            )
            media_input.send_keys(os.path.abspath(content))
            time.sleep(5)
            
            if caption:
                caption_box = WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="6"]'))
                )
                clear_text_field(caption_box)
                caption_box.send_keys(caption)
                time.sleep(1)
        else:
            text_box = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="6"]'))
            )
            clear_text_field(text_box)
            text_box.send_keys(content)
            time.sleep(1)
        
        if not safe_click(driver, '//span[@data-icon="send"]'):
            raise Exception("Could not click send button")

        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(@aria-label, "Status")]'))
        )
        return True
        
    except Exception as e:
        print(f"Status post failed: {str(e)}")
        return False

def send_group_message(driver, group_name, content, content_type, caption=None):
    """Send message to WhatsApp group with robust error handling"""
    try:
        search_box = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
        )
        clear_text_field(search_box)
        search_box.send_keys(group_name)
        time.sleep(3)

        group_xpath = f'//span[@title="{group_name}"]'
        group_element = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, group_xpath))
        )
        group_element.click()
        time.sleep(3)

        if content_type == "media":
            if not os.path.exists(content):
                raise FileNotFoundError(f"Media not found: {content}")
            
            if not safe_click(driver, '//div[@title="Attach"]'):
                raise Exception("Could not click attach button")
            
            time.sleep(1)
            media_input = driver.find_element(By.XPATH, '//input[@accept="image/*,video/*"]')
            media_input.send_keys(os.path.abspath(content))
            time.sleep(3)
            
            if caption:
                caption_box = WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                )
                clear_text_field(caption_box)
                caption_box.send_keys(caption)
                time.sleep(1)
        else:
            message_box = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )
            clear_text_field(message_box)
            message_box.send_keys(content)
            time.sleep(1)
        
        if not safe_click(driver, '//span[@data-icon="send"] | //button[@aria-label="Send"]'):
            raise Exception("Could not click send button")
        
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, '//span[@data-icon="msg-check"]'))
        )
        return True
        
    except Exception as e:
        print(f"Group message failed for '{group_name}': {str(e)}")
        return False

def execute_task(task):
    """Execute task with comprehensive error handling"""
    try:
        if not task.profiles:
            raise ValueError("No profiles specified")
        if task.task_type == "group_message" and not task.targets:
            raise ValueError("No targets specified")

        task.status = "running"
        save_tasks(load_tasks())

        for profile in task.profiles:
            driver = None
            try:
                driver = launch_driver(profile)
                driver.get("https://web.whatsapp.com")
                time.sleep(20)
                
                if task.task_type == "status":
                    success = post_status(driver, task.content, task.content_type, task.caption)
                else:
                    success = True
                    sent_groups = set()
                    for group in task.targets:
                        if group in sent_groups:
                            continue
                        if not send_group_message(driver, group, task.content, task.content_type, task.caption):
                            success = False
                        else:
                            sent_groups.add(group)
                
                task.status = "completed" if success else "failed"
                task.last_error = "" if success else "Some messages failed"
                
            except Exception as e:
                task.status = "failed"
                task.last_error = str(e)
                print(f"Profile {profile} failed: {str(e)}")
                
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass

        save_tasks(load_tasks())

    except Exception as e:
        print(f"Task execution failed: {str(e)}")
        task.status = "failed"
        task.last_error = str(e)
        save_tasks(load_tasks())

if __name__ == "__main__":
    tasks = load_tasks()
    for task in tasks:
        if task.status == "pending" and (not task.schedule_time or datetime.now() >= datetime.fromisoformat(task.schedule_time)):
            execute_task(task)