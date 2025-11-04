import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import Base, engine, get_db
from models import User, Attendance, DailyTask
from auth import router as auth_router, get_current_user
from geo import nearest_branch
from notion_utils import send_attendance, send_task

Base.metadata.create_all(bind=engine)
app = FastAPI(title="MCG Attendance Portal")
app.include_router(auth_router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse("static/index.html")

class Geopoint(BaseModel):
    lat: float; lon: float

class AttendanceIn(Geopoint):
    action: str  # CHECKIN or CHECKOUT

@app.post("/attendance")
def attendance(payload: AttendanceIn, db: Session = Depends(get_db), me: User = Depends(get_current_user())):
    nb = nearest_branch(payload.lat, payload.lon)
    if not nb:
        raise HTTPException(400, "Branches not configured")
    inside = nb["distance_m"] <= nb["radius_m"]
    if not inside:
        raise HTTPException(403, f"You are {int(nb['distance_m'])}m away from {nb['name']}. Move closer.")
    rec = Attendance(user_id=me.id, branch=nb["name"], action=payload.action.upper(),
                     lat=payload.lat, lon=payload.lon, distance_m=nb["distance_m"])
    db.add(rec); db.commit(); db.refresh(rec)
    try:
        send_attendance(me.full_name, me.id, rec.action, rec.branch, True)
    except Exception:
        pass
    return {"ok": True, "branch": rec.branch, "distance_m": rec.distance_m}

class TaskIn(BaseModel):
    title: str; description: str

@app.post("/tasks")
def create_task(payload: TaskIn, db: Session = Depends(get_db), me: User = Depends(get_current_user())):
    task = DailyTask(user_id=me.id, title=payload.title.strip(), description=payload.description.strip())
    db.add(task); db.commit(); db.refresh(task)
    try:
        send_task(me.full_name, me.id, task.title, task.description)
    except Exception:
        pass
    return {"ok": True, "task_id": task.id}

@app.get("/health")
def health():
    return {"ok": True, "env": os.getenv("ENV","dev")}
from fastapi import Response

@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)
