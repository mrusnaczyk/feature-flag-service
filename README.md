# Feature Flag Service

## Overview
### `main.py`
Contains the main API service code

### `db.py`
Contains the db init and persistance layer code

### `seed_db.py`
Seeds the DB with the data of your choosing. Simply run it separately prior to starting the service using `python3 seed_db.py`


## Running the service
From the main workspace directory:
- `source feature-flag-service/bin/activate`
- `export FLASK_APP=main.py`
- `python -m flask run`


## Database
SQLite is used for persisting the data, and the file is under the `/data/` folder.