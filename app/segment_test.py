from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal
import os
import httpx
from datetime import datetime, timedelta

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/segment-test")
async def segment_test(db: Session = Depends(get_db)):
    segment_id = 34688483
    user = db.query(User).first()
    if not user:
        return {"error": "No users in the database"}

    access_token = user.access_token
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        # Get segment metadata
        seg_resp = await client.get(
            f"https://www.strava.com/api/v3/segments/{segment_id}",
            headers=headers
        )
        if seg_resp.status_code != 200:
            return {
                "error": "Failed to fetch segment metadata",
                "status_code": seg_resp.status_code,
                "details": seg_resp.text
            }

        segment = seg_resp.json()
        effort_count_total = segment.get("effort_count")

        # Get all user efforts
        eff_resp = await client.get(
            f"https://www.strava.com/api/v3/segments/{segment_id}/all_efforts",
            headers=headers
        )
        if eff_resp.status_code != 200:
            return {
                "error": "Failed to fetch user efforts",
                "status_code": eff_resp.status_code,
                "details": eff_resp.text  # Debug line
            }

        efforts = eff_resp.json()

        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)

        efforts_last_30 = [
            e for e in efforts
            if datetime.strptime(e["start_date"], "%Y-%m-%dT%H:%M:%SZ") > thirty_days_ago
        ]

        if efforts:
            fastest_effort = min(efforts, key=lambda x: x["elapsed_time"])
            best_time = fastest_effort["elapsed_time"]
            best_date = fastest_effort["start_date"]
        else:
            best_time = None
            best_date = None

        return {
            "segment_name": segment.get("name"),
            "effort_count_total": effort_count_total,
            "user_effort_total": len(efforts),
            "user_efforts_last_30_days": len(efforts_last_30),
            "user_fastest_effort_seconds": best_time,
            "user_fastest_effort_date": best_date
        }
