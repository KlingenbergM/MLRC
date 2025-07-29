from fastapi import APIRouter

router = APIRouter()

@router.get("/leaderboard")
def get_leaderboard():
    return [
        {"rank": 1, "name": "Alice", "time": "5:32"},
        {"rank": 2, "name": "Bob", "time": "5:45"}
    ]
