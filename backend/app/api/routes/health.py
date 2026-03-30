from fastapi import APIRouter

from app.db.mongodb import get_mongo_status

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "scm-milp-poc-backend",
        "mongodb": get_mongo_status(),
    }
