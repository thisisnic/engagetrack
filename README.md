# EngageTrack

EngageTrack is a tool designed to help Open Source maintainers measure and visualise community engagement. It aggregates and analyses metrics like:

- **Top contributors**: Contributors by code commits

More to be added soon!

## Features

- **Flask App**: UI to interact with API
- **Flask API**: Endpoints to manage repositories and fetch metrics.
- **Asynchronous Data Fetching**: Efficiently gather data from GitHub.

## Installation

```bash
# Clone the repository
git clone https://github.com/thisisnic/engagetrack.git
cd engagetrack

# Install dependencies
pip install -r requirements.txt

# Initialise the database
python -c "from app import db; db.create_all()"

# Run the Flask app
python -c "from app import app; app.run(debug=True)"
```

## API Endpoints

* Add Repository: POST /repos
* List Repositories: GET /repos
* Delete Repository: DELETE /repos/<repo_id>
* Get Metrics: GET /metrics
* Refresh Metrics for Repo POST	/repos/<repo_id>/refresh	
