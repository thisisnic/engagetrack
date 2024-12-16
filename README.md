# EngageTrack

EngageTrack is a toy project and tool designed to help Open Source maintainers measure contributors by code commits

More to be added soon!

## Components 

- Flask App
- Flask API

## Installation

```bash
# Clone the repo
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
