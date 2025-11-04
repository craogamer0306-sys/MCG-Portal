from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="EMP")
    created_at = Column(DateTime, default=datetime.utcnow)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    branch = Column(String(80))
    action = Column(String(20))
    lat = Column(Float); lon = Column(Float); distance_m = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")

class DailyTask(Base):
    __tablename__ = "daily_tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255)); description = Column(String(4000))
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")

__table_args__ = (UniqueConstraint('user_id','created_at', name='uniq_user_time'),)
