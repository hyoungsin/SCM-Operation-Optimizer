from app.core.config import MONGODB_DB_NAME, MONGODB_URI


def get_mongo_status() -> dict[str, str]:
    return {
        "enabled": "placeholder",
        "uri": MONGODB_URI,
        "database": MONGODB_DB_NAME,
    }
