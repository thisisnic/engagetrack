# EngageTrack

EngageTrack is a tool designed to help Open Source maintainers measure and visualise community engagement. It aggregates and analyses metrics like:

- **Top contributors**: Code commits, reviews, comments.

Future planned features:

- **Issue response times**: Average time to respond to issues or PRs.
- **Resolution rates**: Trends of open vs. closed issues/PRs over time.

## Features

- **Flask API**: Endpoints to manage repositories and fetch metrics.
- **Asynchronous Data Fetching**: Efficiently gather data from GitHub.
- **CLI Tool**: Interact with EngageTrack via the command line.

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

## Usage

### CLI Tool

## Add a repository to track
python cli/main.py add octocat/Hello-World

## Fetch engagement metrics and generate charts
python cli/main.py metrics octocat/Hello-World

### API Endpoints

* Add Repository: POST /repos
* List Repositories: GET /repos
* Delete Repository: DELETE /repos/<repo_id>
* Get Metrics: GET /metrics
* Refresh Metrics for Repo POST	/repos/<repo_id>/refresh	
