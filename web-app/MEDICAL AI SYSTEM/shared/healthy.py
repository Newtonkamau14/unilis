from datetime import datetime, UTC

from fastapi import APIRouter

router = APIRouter(
    tags=["Health"]
)


@router.get(
    "/health"
)
async def health_check():

    return {
        "status": "healthy",
        "timestamp": (
            datetime.now(
                UTC
            ).isoformat()
        )
    }


@router.get(
    "/ready"
)
async def readiness_check():

    return {
        "status": "ready"
    }


@router.get(
    "/live"
)
async def liveness_check():

    return {
        "status": "alive"
    }