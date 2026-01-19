from pymongo import MongoClient
from pymongo.database import Database
from django.conf import settings

_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    global _client
    if _client is None:
        if not settings.MONGO_DB_URI:
            raise RuntimeError("MONGO_DB_URI is not configured")
        _client = MongoClient(settings.MONGO_DB_URI)
    return _client


def get_mongo_database() -> Database:
    return get_mongo_client().get_default_database()
