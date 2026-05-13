from fastapi import APIRouter

router = APIRouter(tags=["support"])


@router.get(
    "/check-server",
    summary="Check Server",
    description="Health check endpoint that confirms the API server is running.",
)
async def check_server():
    return {"message": "Server đang chạy ổn định!"}
