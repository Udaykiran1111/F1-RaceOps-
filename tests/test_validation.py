
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pymongo.errors import WriteError

from raceops.config import MONGODB_DB, MONGODB_URI
from raceops.validation import VALIDATORS
from pymongo.errors import DuplicateKeyError
from raceops.db import ensure_indexes

@pytest.fixture(scope="module")
def telemetry_test_collection():
    from pymongo import MongoClient

    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=3000,
    )
    client.admin.command("ping")

    db = client[MONGODB_DB]
    name = f"_test_telemetry_validation_{uuid4().hex}"

    db.create_collection(
        name,
        validator=VALIDATORS["telemetry"],
        validationLevel="strict",
        validationAction="error",
    )

    yield db[name]

    db.drop_collection(name)
    client.close()


def valid_event():
    return {
        "event_id": str(uuid4()),
        "race_id": "RACE-TEST",
        "driver_id": "D01",
        "timestamp": datetime.now(timezone.utc),
        "lap": 1,
        "speed_kmh": 250.0,
        "tyre_compound": "MEDIUM",
        "tyre_age": 5,
    }


def test_valid_telemetry_is_accepted(telemetry_test_collection):
    event = valid_event()

    result = telemetry_test_collection.insert_one(event)

    assert telemetry_test_collection.find_one(
        {"_id": result.inserted_id}
    ) is not None


def test_missing_required_field_is_rejected(
    telemetry_test_collection,
):
    event = valid_event()
    del event["speed_kmh"]

    with pytest.raises(WriteError):
        telemetry_test_collection.insert_one(event)


def test_invalid_tyre_compound_is_rejected(
    telemetry_test_collection,
):
    event = valid_event()
    event["tyre_compound"] = "ULTRA_SOFT"

    with pytest.raises(WriteError):
        telemetry_test_collection.insert_one(event)


def test_speed_above_limit_is_rejected(
    telemetry_test_collection,
):
    event = valid_event()
    event["speed_kmh"] = 400.0

    with pytest.raises(WriteError):
        telemetry_test_collection.insert_one(event)


def test_invalid_timestamp_type_is_rejected(
    telemetry_test_collection,
):
    event = valid_event()
    event["timestamp"] = "2026-10-18T12:00:00Z"

    with pytest.raises(WriteError):
        telemetry_test_collection.insert_one(event)
def test_duplicate_event_id_is_rejected(telemetry_test_collection):
    telemetry_test_collection.create_index(
    [("event_id", 1)],
    unique=True,
)

    event = valid_event()
    telemetry_test_collection.insert_one(event)

    duplicate = event.copy()
    duplicate.pop("_id", None)

    with pytest.raises(DuplicateKeyError):
        telemetry_test_collection.insert_one(duplicate)