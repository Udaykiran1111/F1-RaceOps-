import argparse
from raceops.db import get_client, get_db, ping
from raceops.simulator import run_stream
from raceops.config import SIMULATION_INTERVAL_SECONDS
p=argparse.ArgumentParser(description="Generate continuous synthetic F1 telemetry.")
p.add_argument("--interval",type=float,default=SIMULATION_INTERVAL_SECONDS)
p.add_argument("--events",type=int,default=None,help="Stop after this many events; default runs until Ctrl+C")
a=p.parse_args()
client=get_client()
try:
    db=get_db(client); ping(db)
    run_stream(db, interval=a.interval, stop_after=a.events)
except KeyboardInterrupt:
    print("\nSimulator stopped.")
finally:
    client.close()
