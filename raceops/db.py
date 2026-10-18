from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError
from .config import MONGODB_URI, MONGODB_DB

COLLECTIONS = ["races", "drivers", "telemetry", "pit_stops", "incidents", "strategy_decisions"]

def get_client():
    return MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)

def get_db(client=None):
    client = client or get_client()
    return client[MONGODB_DB]

def ensure_indexes(db):
    db.drivers.create_index([("driver_id", ASCENDING)], unique=True)
    db.races.create_index([("race_id", ASCENDING)], unique=True)
    db.telemetry.create_index([("race_id", ASCENDING), ("driver_id", ASCENDING), ("timestamp", DESCENDING)])
    db.telemetry.create_index([("timestamp", DESCENDING)])
    db.telemetry.create_index([("event_id", ASCENDING)], unique=True)
    db.pit_stops.create_index([("race_id", ASCENDING), ("driver_id", ASCENDING)])
    db.incidents.create_index([("race_id", ASCENDING), ("lap", ASCENDING)])
    db.strategy_decisions.create_index([("race_id", ASCENDING), ("timestamp", DESCENDING)])
    return True

def ping(db):
    db.command("ping")
    return True
