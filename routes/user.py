from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}")
async def get_user(user_id: str):
    return {"user_id": user_id}
