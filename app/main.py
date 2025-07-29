from fastapi import FastAPI
from app.auth import router as auth_router
from app.leaderboard import router as leaderboard_router
from database import engine
from models import Base

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
    return db.query(User).all()
