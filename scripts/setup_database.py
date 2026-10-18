from raceops.db import get_client, get_db, ping
from raceops.validation import install_validators
from raceops.seed import seed_database
from raceops.db import ensure_indexes
if __name__ == "__main__":
    client=get_client()
    try:
        db=get_db(client); ping(db)
        install_validators(db); ensure_indexes(db)
        print("MongoDB connection: OK")
        print("Seed summary:", seed_database(db))
        print("Setup complete. Database: f1_raceops")
    finally:
        client.close()
