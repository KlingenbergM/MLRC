from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx, os, datetime

from app.database import SessionLocal
from app.models import User

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/login")
def login():
    client_id = os.getenv("STRAVA_CLIENT_ID")
    redirect_uri = os.getenv("STRAVA_CALLBACK_URL")
    auth_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&approval_prompt=auto&scope=read,activity:read_all"
    return RedirectResponse(auth_url)

@router.get("/callback")
async def callback(code: str, db: Session = Depends(get_db)):
    client_id = os.getenv("STRAVA_CLIENT_ID")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET")
    redirect_uri = os.getenv("STRAVA_CALLBACK_URL")
    token_url = "https://www.strava.com/oauth/token"
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code"
        })

    data = response.json()
    strava_id = data.get("athlete", {}).get("id")
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    expires_at = datetime.datetime.fromtimestamp(data.get("expires_at"))

    # Save or update user in DB
    user = db.query(User).filter(User.strava_id == strava_id).first()
    if user:
        user.access_token = access_token
        user.refresh_token = refresh_token
        user.expires_at = expires_at
    else:
        user = User(
            strava_id=strava_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        db.add(user)
    db.commit()

    return {"message": "Authentication successful", "user": {"strava_id": strava_id}}

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "strava_id": user.strava_id,
            "access_token": user.access_token,
            "expires_at": user.expires_at,
        }
        for user in users
    ]
