from fastapi import APIRouter
from fastapi.responses import RedirectResponse
import httpx, os

router = APIRouter()

@router.get("/login")
def login():
    client_id = os.getenv("STRAVA_CLIENT_ID")
    redirect_uri = os.getenv("STRAVA_CALLBACK_URL")
    auth_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&approval_prompt=auto&scope=read,activity:read_all"
    return RedirectResponse(auth_url)

@router.get("/callback")
async def callback(code: str):
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
    return {"message": "Authentication successful", "data": response.json()}
