from pprint import pprint
from raceops.db import get_client, get_db
from raceops.aggregations import driver_pace_summary, compound_performance, pit_loss_by_team, incident_summary, strategy_action_counts
client=get_client()
try:
 db=get_db(client)
 for title,fn in [("DRIVER PACE",driver_pace_summary),("TYRE COMPOUND PERFORMANCE",compound_performance),
                  ("PIT STOP ANALYSIS",pit_loss_by_team),("INCIDENT SUMMARY",incident_summary),
                  ("STRATEGY ACTION COUNTS",strategy_action_counts)]:
  print("\n==",title,"=="); pprint(fn(db))
finally: client.close()
