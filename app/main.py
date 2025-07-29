from fastapi import FastAPI
from app.auth import router as auth_router
from app.leaderboard import router as leaderboard_router
from database import engine
from models import Base
from app.segment_test import router as segment_test_router
app.include_router(segment_test_router)


Base.metadata.create_all(bind=engine)


app = FastAPI()

@app.get("/")
def root():
    return {"message": "App is running!"}

app.include_router(auth_router)
app.include_router(leaderboard_router)
