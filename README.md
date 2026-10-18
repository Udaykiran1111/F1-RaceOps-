# F1 RaceOps

**Race Operations, Synthetic Telemetry & Strategy Analytics**  
Course project: CSE494 — Intelligent NoSQL Databases

> **Data notice:** This project generates synthetic demonstration telemetry and event records. It is not connected to official live Formula 1 telemetry. Strategy outputs are rule-based and illustrative, not professional race-engineering advice.

## Features

- Create races and update race status.
- Register and manage driver records.
- Generate timestamped synthetic telemetry for a selected race and driver.
- Record pit stops and incidents.
- Store documents in MongoDB through PyMongo.
- Apply MongoDB JSON Schema validators and indexes.
- Run aggregation pipelines for driver pace, tyre compound performance, pit-stop summaries, incident summaries, and strategy-action counts.
- Display summaries and charts in Streamlit.
- Run automated strategy and telemetry-validation tests.

## Stack

Python, MongoDB, PyMongo, Streamlit, Pandas/charting dependencies from `requirements.txt`, and pytest.

## Project structure

```text
F1_RaceOps/
├── app.py
├── raceops/
│   ├── config.py
│   ├── db.py
│   ├── validation.py
│   ├── simulator.py
│   ├── strategy.py
│   ├── aggregations.py
│   └── crud.py
├── scripts/
│   ├── setup_database.py
│   ├── demo_crud.py
│   ├── run_aggregations.py
│   └── run_simulator.py
├── tests/
│   ├── test_strategy.py
│   └── test_validation.py
├── report/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Verify the exact filenames against your final repository before pushing.

## Requirements

- Python 3.10 or newer (the tested local environment used Python 3.13.11).
- A running MongoDB server, local or hosted.
- Git, if uploading to GitHub.

## Install on Windows

```cmd
cd /d D:\Downloads\F1_RaceOps
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Configure a local `.env` file using the variable names expected by `raceops/config.py`. The example below is only valid if the project reads these exact names:

```dotenv
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=f1_raceops
```

Check `raceops/config.py` before using the example. Do not commit `.env` or real credentials.

Initialize the database:

```cmd
set PYTHONPATH=.
python scripts\setup_database.py
```

## Run the Streamlit application

With the virtual environment activated and MongoDB running:

```cmd
set PYTHONPATH=.
python -m streamlit run app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`.

## Demonstration workflow

1. Open **Race Management** and create a race with a unique race ID.
2. Open **Driver Management** and register a driver or select an existing driver.
3. Open **Simulator & Events**, select a race and driver, and generate a small number of telemetry events.
4. Open **Race Dashboard** and inspect counts, pace summaries, tyre compound analytics, latest telemetry, and strategy-action distribution.
5. Record a pit stop and an incident.
6. Use MongoDB Compass to inspect documents in `races`, `drivers`, `telemetry`, `pit_stops`, `incidents`, and `strategy_decisions`.

## Run tests

```cmd
set PYTHONPATH=.
python -m pytest -v
```

The documented local run returned **10 passed**: four strategy tests and six telemetry-validation tests. Run tests again after any code changes.

## Useful scripts

```cmd
python scripts\demo_crud.py
python scripts\run_aggregations.py
python scripts\run_simulator.py --interval 1 --events 30
```

Set `PYTHONPATH=.` in the same Command Prompt session if package imports require it.

## MongoDB collections

| Collection | Purpose |
|---|---|
| `races` | Race metadata and status |
| `drivers` | Driver identity and team details |
| `telemetry` | Timestamped synthetic observations |
| `pit_stops` | Pit-stop event records |
| `incidents` | Incident event records |
| `strategy_decisions` | Rule-based strategy recommendations |

The telemetry collection has a unique index on `event_id`, plus indexes for race/driver/time queries and timestamp ordering.

## GitHub safety

Do not commit:
- `.env` or database credentials
- `.venv/`
- `__pycache__/` or `.pytest_cache/`
- database dumps, exports, or secrets

Commit `.env.example` with placeholder values only. Review `git status` before every push.

## Deployment

The Streamlit interface can be hosted on Streamlit Community Cloud, but a hosted app cannot reach MongoDB running only on the developer's `localhost`. Deployment requires a reachable database such as MongoDB Atlas, correct network access rules, and credentials stored in the hosting platform's secrets manager. Configure the application to read deployed secrets securely and test the hosted workflow before claiming deployment is complete.

## Limitations

- Data is synthetic, not official live F1 telemetry.
- Strategy recommendations are rule-based and illustrative.
- Cloud deployment requires separate database and secrets configuration.
- MongoDB cross-collection references are application-managed rather than relational foreign keys.
