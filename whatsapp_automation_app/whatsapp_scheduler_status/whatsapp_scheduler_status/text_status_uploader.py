import tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from threading import Thread
import time, os, platform

# Auto-detect Chrome user data path
if platform.system() == "Windows":
    BASE_USER_DATA_DIR = os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data")
elif platform.system() == "Darwin":
    BASE_USER_DATA_DIR = os.path.expanduser("~/Library/Application Support/Google/Chrome")
elif platform.system() == "Linux":
    BASE_USER_DATA_DIR = os.path.expanduser("~/.config/google-chrome")
else:
    raise RuntimeError("Unsupported OS")

def post_text_status(profile_name, status_text):
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={BASE_USER_DATA_DIR}")
    options.add_argument(f"--profile-directory={profile_name}")
    driver = webdriver.Chrome(options=options)
    driver.get("https://web.whatsapp.com")
    time.sleep(10)
    try:
        driver.find_element(By.CSS_SELECTOR, "span[data-icon='status-v3-unread']").click()
        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR, "div[title='Click to add status update']").click()
        time.sleep(2)
        textbox = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
        textbox.send_keys(status_text)
        textbox.send_keys(Keys.ENTER)
        print(f"Status posted from {profile_name}")
    except Exception as e:
        print(f"Error posting status on {profile_name}:", e)
    time.sleep(5)
    driver.quit()

def upload_status(status_text):
    threads = []
    for i in range(10):
        profile = f"Profile {i+1}"
        t = Thread(target=post_text_status, args=(profile, status_text))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

def on_click():
    text = status_entry.get("1.0", tk.END).strip()
    Thread(target=upload_status, args=(text,)).start()

root = tk.Tk()
root.title("Text Status Uploader")

tk.Label(root, text="Enter Status Text:").pack()
status_entry = tk.Text(root, height=4, width=50)
status_entry.pack()
status_entry.insert(tk.END, "This is my status!")

tk.Button(root, text="Upload Status", command=on_click).pack(pady=10)
root.mainloop()
