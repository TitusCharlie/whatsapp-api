from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import threading
import time
from datetime import datetime
from full_auto_scheduler import Task, load_tasks, save_tasks, execute_task, launch_driver

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change in production

# ====================
# CONFIGURATION
# ====================
BASE_AUTOMATION_PROFILE_PATH = os.path.join(os.path.expanduser("~"), "Documents", "AutomationProfile")
TASKS_FILE = 'tasks.json'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}
scheduler_running = False
scheduler_thread = None

# ====================
# HELPER FUNCTIONS
# ====================

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_available_profiles():
    """Get list of available Chrome profiles"""
    if os.path.exists(BASE_AUTOMATION_PROFILE_PATH):
        return [name for name in os.listdir(BASE_AUTOMATION_PROFILE_PATH)
                if os.path.isdir(os.path.join(BASE_AUTOMATION_PROFILE_PATH, name))]
    return []

def ensure_base_folder():
    """Ensure the base profile directory exists"""
    if not os.path.exists(BASE_AUTOMATION_PROFILE_PATH):
        os.makedirs(BASE_AUTOMATION_PROFILE_PATH)

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ====================
# ROUTES
# ====================

@app.route('/')
def home():
    return redirect(url_for('view_tasks'))

@app.route('/tasks')
def view_tasks():
    status_filter = request.args.get('status')
    tasks = load_tasks()
    if status_filter in ['pending', 'completed', 'failed']:
        tasks = [t for t in tasks if t.status == status_filter]
    return render_template('view_tasks.html', 
                         tasks=tasks, 
                         status_filter=status_filter, 
                         scheduler_running=scheduler_running)

@app.route('/create', methods=['GET', 'POST'])
def create_task():
    if request.method == 'GET':
        return render_template('create_task.html', profiles=get_available_profiles())
    
    try:
        # Get form data
        task_type = request.form.get('task_type')
        content = request.form.get('content')
        targets = [t.strip() for t in request.form.get('targets', '').split(',') if t.strip()]
        profiles = request.form.getlist('profiles')
        schedule_time = request.form.get('schedule_time')
        caption = request.form.get('caption')
        
        # Handle file upload
        media_path = None
        if 'media' in request.files:
            media = request.files['media']
            if media.filename != '' and allowed_file(media.filename):
                filename = secure_filename(media.filename)
                media_path = os.path.join(UPLOAD_FOLDER, filename)
                media.save(media_path)
                # Store relative path for portability
                media_path = os.path.join(UPLOAD_FOLDER, filename)
            elif media.filename != '':
                flash('Invalid file type. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS), 'danger')
                return redirect(url_for('create_task'))
        
        # Determine content type
        content_type = 'media' if media_path else 'text'
        
        # Create task
        new_task = Task(
            task_type=task_type,
            content=content,
            content_type=content_type,
            targets=targets,
            profiles=profiles,
            schedule_time=schedule_time,
            caption=caption,
            media_path=media_path
        )
        
        # Save task
        tasks = load_tasks()
        tasks.append(new_task)
        save_tasks(tasks)
        
        flash('Task created successfully!', 'success')
        return redirect(url_for('view_tasks'))
        
    except Exception as e:
        flash(f'Error creating task: {str(e)}', 'danger')
        return redirect(url_for('create_task'))

@app.route("/run-task/<task_id>", methods=["POST"])
def run_task_now(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t.id == task_id), None)
    if task:
        threading.Thread(target=execute_task, args=(task,)).start()
    return redirect(url_for('view_tasks'))

@app.route('/start-scheduler', methods=['POST'])
def start_scheduler():
    global scheduler_running, scheduler_thread

    def scheduler_loop():
        while scheduler_running:
            tasks = load_tasks()
            now = datetime.now()
            for task in tasks:
                try:
                    if not task.schedule_time or task.status != "pending":
                        continue
                    
                    # Handle both string and datetime schedule_time
                    if isinstance(task.schedule_time, str):
                        task_time = datetime.fromisoformat(task.schedule_time) if 'T' in task.schedule_time \
                                   else datetime.strptime(task.schedule_time, "%Y-%m-%d %H:%M")
                    else:
                        task_time = task.schedule_time
                    
                    if now >= task_time:
                        threading.Thread(target=execute_task, args=(task,)).start()
                        
                except Exception as e:
                    print(f"[Scheduler] Error with task {task.id}: {e}")
                    task.status = "failed"
                    task.last_error = str(e)
            
            save_tasks(tasks)
            time.sleep(60)

    if not scheduler_running:
        scheduler_running = True
        scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        scheduler_thread.start()
        flash("Scheduler started", 'success')
    else:
        flash("Scheduler is already running", 'info')
    return redirect(url_for('view_tasks'))

@app.route('/stop-scheduler', methods=['POST'])
def stop_scheduler():
    global scheduler_running
    if scheduler_running:
        scheduler_running = False
        flash("Scheduler stopped", 'success')
    else:
        flash("Scheduler wasn't running", 'info')
    return redirect(url_for('view_tasks'))

@app.route('/retry-task/<task_id>', methods=['POST'])
def retry_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task.id == task_id and task.status == 'failed':
            task.status = 'pending'
            task.last_error = None
            flash(f"Task {task_id} set to pending", 'success')
            break
    else:
        flash(f"Task {task_id} not found or not failed", 'danger')
    save_tasks(tasks)
    return redirect(url_for('view_tasks'))

@app.route('/delete-task/<task_id>', methods=['POST'])
def delete_task(task_id):
    tasks = load_tasks()
    initial_count = len(tasks)
    tasks = [t for t in tasks if t.id != task_id]
    if len(tasks) < initial_count:
        save_tasks(tasks)
        flash(f"Task {task_id} deleted", 'success')
    else:
        flash(f"Task {task_id} not found", 'danger')
    return redirect(url_for('view_tasks'))

@app.route('/scan', methods=['GET', 'POST'])
def scan_qr():
    ensure_base_folder()
    if request.method == 'POST':
        profile = request.form['new_profile'].strip()
        if profile:
            profile_path = os.path.join(BASE_AUTOMATION_PROFILE_PATH, profile)
            if not os.path.exists(profile_path):
                os.makedirs(profile_path)
            
            driver = launch_driver(profile)
            driver.get("https://web.whatsapp.com")
            flash(f"Scan QR for profile '{profile}' (will auto-close in 60s)", 'info')
            threading.Thread(
                target=lambda: (time.sleep(60), driver.quit()),
                daemon=True
            ).start()
    
    profiles = get_available_profiles()
    return render_template('scan.html', profiles=profiles)

@app.route('/edit-task/<task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t.id == task_id), None)
    if not task:
        flash("Task not found", 'danger')
        return redirect(url_for('view_tasks'))

    if request.method == 'POST':
        try:
            # Update task details
            task.task_type = request.form['task_type']
            task.schedule_time = request.form['schedule_time']
            task.profiles = request.form.getlist('profiles')
            task.content = request.form.get('content', '').strip()
            
            # Handle media update
            if 'media' in request.files:
                media = request.files['media']
                if media.filename != '' and allowed_file(media.filename):
                    filename = secure_filename(media.filename)
                    media_path = os.path.join(UPLOAD_FOLDER, filename)
                    media.save(media_path)
                    task.content_type = 'media'
                    task.media_path = os.path.join(UPLOAD_FOLDER, filename)
                elif media.filename != '':
                    flash('Invalid file type', 'danger')
                    return redirect(url_for('edit_task', task_id=task_id))
            
            # Update targets if group message
            if task.task_type == 'group_message':
                task.targets = [t.strip() for t in request.form['targets'].split(',') if t.strip()]
            
            # Update caption
            task.caption = request.form.get('caption', '').strip() or None
            
            save_tasks(tasks)
            flash("Task updated successfully", 'success')
            return redirect(url_for('view_tasks'))
        
        except Exception as e:
            flash(f"Error updating task: {str(e)}", 'danger')
    
    return render_template('edit_task.html', 
                         task=task, 
                         profiles=get_available_profiles(),
                         allowed_extensions=ALLOWED_EXTENSIONS)

if __name__ == '__main__':
    app.run(debug=True)