from fastapi import FastAPI
from app.auth import router as auth_router
from app.leaderboard import router as leaderboard_router

app = FastAPI()

# ✅ This is the important part
@app.get("/")
def root():
    return {"message": "App is running!"}

app.include_router(auth_router)
app.include_router(leaderboard_router)
