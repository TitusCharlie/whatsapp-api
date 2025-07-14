import json
import os
from datetime import datetime

TASKS_FILE = "tasks.json"

def check_task_datetime_format():
    if not os.path.exists(TASKS_FILE):
        print(f"❌ File '{TASKS_FILE}' not found in: {os.getcwd()}")
        return

    with open(TASKS_FILE, 'r') as f:
        try:
            tasks = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ JSON error: {e}")
            return

    if not tasks:
        print("⚠️ tasks.json is empty.")
        return

    print(f"✅ Found {len(tasks)} task(s)\n")

    for task in tasks:
        task_id = task.get("id", "unknown_id")
        schedule_time = task.get("schedule_time")

        print(f"Task ID: {task_id}")
        print(f"Raw schedule_time: {schedule_time}")

        if not schedule_time:
            print("❌ schedule_time is missing.\n")
            continue

        formats_to_try = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%d-%m-%Y %H:%M",
        ]

        parsed = False
        for fmt in formats_to_try:
            try:
                dt = datetime.strptime(schedule_time, fmt)
                print(f"✔ Parsed with format: {fmt} → {dt}\n")
                parsed = True
                break
            except ValueError:
                continue

        if not parsed:
            print("❌ Failed to parse schedule_time with known formats.\n")

if __name__ == "__main__":
    check_task_datetime_format()
