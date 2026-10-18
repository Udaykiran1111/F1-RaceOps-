# F1 RaceOps
**Race Strategy Intelligence & Live Decision Support Platform**  
Course: CSE494 — Intelligent NoSQL Databases

## What this is
F1 RaceOps is an executable, individual-project demonstration of a MongoDB-backed race operations system. A Python simulator emits synthetic telemetry events continuously; PyMongo writes events to MongoDB; aggregation pipelines compute driver pace, tyre-compound summaries, pit-stop analysis, incident counts, and strategy action distributions; a Streamlit dashboard displays the current stored state.

**Data integrity:** all generated race telemetry is explicitly labelled synthetic/simulated. This is not official live F1 telemetry and is not a validated professional strategy model.

## Requirements mapped to the assignment
- MongoDB document model: races, drivers, telemetry, pit_stops, incidents, strategy_decisions.
- MongoDB JSON Schema validators on core collections.
- CRUD: `raceops/crud.py` and `scripts/demo_crud.py`.
- PyMongo integration throughout the application.
- Aggregation: `$match`, `$group`, `$avg`, `$max`, `$sort`, `$lookup`, `$unwind`, `$addFields`.
- Continuous ingestion: `scripts/run_simulator.py`.
- Dashboard: `streamlit run app.py`.
- Optional MongoDB Change Streams: `python scripts/watch_changes.py` (requires replica set / Atlas).
- Tests: `pytest -q`.

## Setup (Windows PowerShell)
1. Install Python 3.10+ and MongoDB Community Server, or create a MongoDB Atlas database.
2. Open a terminal in this project folder.
3. Create environment and install dependencies:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item .env.example .env
   ```
4. Edit `.env` if your MongoDB URI differs from the local default.
5. Start MongoDB Community Server if using local MongoDB.
6. Initialize schema, indexes, and seed data:
   ```powershell
   python scripts/setup_database.py
   ```
7. Run CRUD demonstration:
   ```powershell
   python scripts/demo_crud.py
   ```
8. Run aggregation outputs:
   ```powershell
   python scripts/run_aggregations.py
   ```
9. Start continuous telemetry in terminal 1:
   ```powershell
   python scripts/run_simulator.py --interval 1
   ```
10. Start dashboard in terminal 2:
   ```powershell
   streamlit run app.py
   ```
Stop the simulator with Ctrl+C.

## Dataset
The seeder creates a reproducible synthetic 2026 demo race, 20 driver records, sample pit stops/incidents, and 1,200 synthetic telemetry documents by default. The simulator adds further events. Values are generated for demonstrating database operations and analytics, not for scientific conclusions about real drivers or teams.

## Database design
- `drivers`: relatively stable entities; one document per driver.
- `races`: race-level metadata and status.
- `telemetry`: append-oriented event documents, indexed by race/driver/time.
- `pit_stops`: one document per stop.
- `incidents`: one document per event.
- `strategy_decisions`: auditable output of the rule-based decision engine.

Telemetry is kept separate rather than embedded in driver documents because event volume grows independently and event history needs time-ordered queries. Stable driver identity is referenced by `driver_id`. This avoids unbounded arrays inside a single document.

## Aggregations
1. Driver pace: average lap time and speed, maximum tyre age, grouped by driver.
2. Compound comparison: average lap time, average tyre age and tyre temperature grouped by compound.
3. Pit-stop analysis: `$lookup` drivers to assign team, then average stop time and position delta by team.
4. Incident analysis: group by incident type and severity.
5. Strategy action distribution: count generated recommendations by action.

## Validation and failure handling
MongoDB server-side validators reject missing required fields, invalid enums, invalid ranges, and incorrect BSON types in validated collections. Unique indexes protect driver and race identifiers. Database connection failures are surfaced by the scripts/dashboard; the simulator can be stopped with Ctrl+C. Change Streams require a replica set; standalone local MongoDB may not support them.

## Limitations and future improvements
- Strategy logic is transparent rule-based logic, not a trained or FIA-approved model.
- The simulator models only a subset of race dynamics and does not reproduce vehicle physics.
- For a production-grade extension: ingest permitted public historical data, calibrate tyre degradation from sourced data, add event replay, use replica-set Change Streams, persist audit trails, add unit/integration tests against MongoDB, and compare strategy outcomes over multiple randomized race scenarios.
