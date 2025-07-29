from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# adjust imports if database/models are in app/ folder
from database import engine, SessionLocal
from models import Base, User

from app.auth import router as auth_router
from app.leaderboard import router as leaderboard_router

app = FastAPI()

# Create DB tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "App is running!"}

app.include_router(auth_router)
app.include_router(leaderboard_router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"strava_id": u.strava_id, "access_token": u.access_token} for u in users]
