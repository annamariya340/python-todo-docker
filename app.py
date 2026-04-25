from flask import Flask, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

TASKS_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def render_html(tasks):
    completed_count = sum(1 for t in tasks if t['completed'])
    uncompleted_count = len(tasks) - completed_count

    def task_row(task):
        is_done = task['completed']
        strike = 'text-decoration:line-through;color:#b0b0b0;' if is_done else 'color:#1a1a2e;'
        cb_bg = '#4f8ef7' if is_done else '#fff'
        cb_border = '#4f8ef7' if is_done else '#d0d0d0'
        checkmark = '&#10003;' if is_done else ''
        return f"""
        <div style="display:flex;align-items:center;gap:12px;
                    background:#fff;border:1.5px solid #ececec;border-radius:12px;
                    padding:13px 16px;margin-bottom:10px;
                    box-shadow:0 2px 8px rgba(79,142,247,0.06);
                    transition:box-shadow 0.2s;">
          <form action="/toggle/{task['id']}" method="POST" style="margin:0;flex-shrink:0;">
            <button type="submit"
              style="width:24px;height:24px;border-radius:6px;
                     border:2px solid {cb_border};background:{cb_bg};
                     color:#fff;font-size:14px;font-weight:700;cursor:pointer;
                     display:flex;align-items:center;justify-content:center;
                     line-height:1;padding:0;">{checkmark}</button>
          </form>
          <span style="flex:1;font-size:15px;font-weight:500;{strike}">{task['title']}</span>
          <form action="/delete/{task['id']}" method="POST" style="margin:0;">
            <button type="submit"
              style="background:#ff5a5a;color:#fff;border:none;border-radius:8px;
                     padding:7px 16px;font-family:'Nunito',sans-serif;font-size:13px;
                     font-weight:700;cursor:pointer;transition:background 0.15s;"
              onmouseover="this.style.background='#e03e3e'"
              onmouseout="this.style.background='#ff5a5a'">Delete</button>
          </form>
        </div>"""

    rows = ''.join(task_row(t) for t in tasks)

    empty = """
        <div style="text-align:center;padding:36px 0 20px;color:#c0c0c0;font-size:14px;">
          <div style="font-size:32px;margin-bottom:8px;">📋</div>
          No tasks yet. Add one above!
        </div>""" if not tasks else ''

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>To Do List</title>
  <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Nunito', sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(145deg, #fde8c8 0%, #fbc8e8 45%, #c8dcfb 100%);
      padding: 24px;
    }}
    .card {{
      background: #ffffff;
      border-radius: 22px;
      padding: 34px 30px 28px;
      width: 100%;
      max-width: 460px;
      box-shadow: 0 12px 48px rgba(100,120,200,0.15), 0 2px 8px rgba(0,0,0,0.06);
    }}
    h1 {{
      text-align: center;
      font-size: 1.75rem;
      font-weight: 800;
      color: #1a1a2e;
      margin-bottom: 22px;
      letter-spacing: -0.01em;
    }}
    .add-form {{
      display: flex;
      gap: 10px;
      margin-bottom: 10px;
    }}
    .add-form input {{
      flex: 1;
      padding: 12px 16px;
      border: 2px solid #e8e8e8;
      border-radius: 11px;
      font-family: 'Nunito', sans-serif;
      font-size: 14px;
      font-weight: 500;
      color: #1a1a2e;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
      background: #fafafa;
    }}
    .add-form input:focus {{
      border-color: #4f8ef7;
      background: #fff;
      box-shadow: 0 0 0 3px rgba(79,142,247,0.12);
    }}
    .add-form input::placeholder {{ color: #c0c0c0; }}
    .add-form button {{
      background: #4f8ef7;
      color: #fff;
      border: none;
      border-radius: 11px;
      padding: 12px 22px;
      font-family: 'Nunito', sans-serif;
      font-weight: 700;
      font-size: 14px;
      cursor: pointer;
      transition: background 0.15s, transform 0.1s;
      white-space: nowrap;
    }}
    .add-form button:hover {{ background: #3a7ae0; }}
    .add-form button:active {{ transform: scale(0.97); }}
    .divider {{
      border: none;
      border-top: 2px solid #f2f2f2;
      margin: 18px 0 16px;
    }}
    .task-label {{
      font-size: 12px;
      font-weight: 700;
      color: #a0a0b0;
      text-transform: uppercase;
      letter-spacing: .1em;
      margin-bottom: 14px;
    }}
    .stats {{
      display: flex;
      justify-content: center;
      gap: 6px;
      margin-top: 18px;
      padding-top: 16px;
      border-top: 2px solid #f2f2f2;
      font-size: 13px;
      font-weight: 600;
      color: #a0a0b0;
    }}
    .stats .pill {{
      background: #f0f5ff;
      color: #4f8ef7;
      border-radius: 20px;
      padding: 3px 12px;
      font-weight: 700;
    }}
    .stats .pill.done {{ background: #f0fff4; color: #34c472; }}
  </style>
</head>
<body>
<div class="card">
  <h1>To Do List</h1>

  <form class="add-form" action="/add" method="POST">
    <input type="text" name="title" placeholder="Add a new task..." autocomplete="off" required/>
    <button type="submit">Add</button>
  </form>

  <hr class="divider"/>

  {"<div class='task-label'>Task List</div>" if tasks else ""}
  {rows}
  {empty}

  <div class="stats">
    <span class="pill done">&#10003; {completed_count} Completed</span>
    <span class="pill">&#9632; {uncompleted_count} Remaining</span>
  </div>
</div>
</body>
</html>"""

@app.route('/')
def index():
    tasks = load_tasks()
    return render_html(tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title', '').strip()
    if title:
        tasks = load_tasks()
        task = {
            'id': int(datetime.now().timestamp() * 1000),
            'title': title,
            'completed': False,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        tasks.append(task)
        save_tasks(tasks)
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break
    save_tasks(tasks)
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t['id'] != task_id]
    save_tasks(tasks)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)