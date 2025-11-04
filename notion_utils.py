import os, requests, datetime
NOTION_TOKEN = os.getenv("NOTION_API_TOKEN")
ATT_DB = os.getenv("NOTION_ATTENDANCE_DB_ID")  # Attendance Records
TASK_DB = os.getenv("NOTION_TASKS_DB_ID")      # Daily Task
BASE = "https://api.notion.com/v1/pages"
HEAD = {"Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"}

def _post(payload):
    if not NOTION_TOKEN: return {"skipped": True}
    r = requests.post(BASE, headers=HEAD, json=payload, timeout=20)
    return {"status": r.status_code, "ok": r.ok}

def send_attendance(full_name, employee_id, action, branch, inside=True):
    if not ATT_DB: return {"skipped": True}
    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
    time_str = now.split("T")[1].replace("Z","")
    payload = {
      "parent":{"database_id": ATT_DB},
      "properties":{
        "Employee Name":{"title":[{"text":{"content": full_name}}]},
        "Employee ID":{"rich_text":[{"text":{"content": str(employee_id)}}]},
        "Date":{"date":{"start": now}},
        "Time":{"rich_text":[{"text":{"content": time_str}}]},
        "Status":{"select":{"name": action}},
        "Office Name":{"select":{"name": branch}},
        "Inside Office":{"checkbox": bool(inside)}
      }
    }
    return _post(payload)

def send_task(full_name, employee_id, title, description):
    if not TASK_DB: return {"skipped": True}
    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
    payload = {
      "parent":{"database_id": TASK_DB},
      "properties":{
        "Employee":{"title":[{"text":{"content": full_name}}]},
        "Employee ID":{"rich_text":[{"text":{"content": str(employee_id)}}]},
        "Date":{"date":{"start": now}},
        "Task Title":{"rich_text":[{"text":{"content": title}}]},
        "Task Description":{"rich_text":[{"text":{"content": description[:1900]}}]},
        "Status":{"select":{"name":"Submitted"}}
      }
    }
    return _post(payload)
