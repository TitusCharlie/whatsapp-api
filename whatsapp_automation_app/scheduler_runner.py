# import threading
# import time
# from datetime import datetime
# from full_auto_scheduler import load_tasks, save_tasks, run_task

# print("[Scheduler] Background task scheduler started.")

# def task_scheduler_loop():
#     while True:
#         tasks = load_tasks()
#         now = datetime.now()
#         for task in tasks:
#             try:
#                 task_time = datetime.strptime(task.schedule_time, "%Y-%m-%d %H:%M")
#                 if task.status == "pending" and now >= task_time:
#                     print(f"[Scheduler] Running task {task.id}...")
#                     threading.Thread(target=run_task, args=(task,)).start()
#             except Exception as e:
#                 print(f"[Scheduler] Error with task {task.id}: {e}")
#         save_tasks(tasks)
#         time.sleep(60)

# if __name__ == "__main__":
#     task_scheduler_loop()