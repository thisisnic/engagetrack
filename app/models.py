from datetime import datetime
from app import db
import os
import requests

GITHUB_TOKEN = os.getenv("GH_API_TOKEN")


class Repo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    url = db.Column(db.String(256), unique=True, nullable=False)
    last_retrieved = db.Column(db.DateTime, default=None)


def save_repo(repo_url):
    # Validate that the repository exists on GitHub
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    github_api_url = f"https://api.github.com/repos/{repo_url}"
    response = requests.get(github_api_url, headers=headers)

    if response.status_code == 404:
        raise ValueError(f"Repository {repo_url} does not exist on GitHub.")
    elif response.status_code != 200:
        raise ValueError(
            f"GitHub API error: {response.status}. Please try again later."
        )

    # Extract repository name from URL
    repo_name = repo_url.split("/")[-1]

    # Check if the repository already exists in the database
    existing_repo = Repo.query.filter_by(url=repo_url).first()
    if existing_repo:
        return existing_repo  # Return the existing repo

    # If it doesn't exist, add it to the database
    repo = Repo(name=repo_name, url=repo_url, last_retrieved=datetime.utcnow())
    db.session.add(repo)
    db.session.commit()
    return repo


def delete_repo(repo_id):
    repo = Repo.query.get(repo_id)
    if repo:
        db.session.delete(repo)
        db.session.commit()
        return True
    return False


def fetch_all_repos():
    repos = Repo.query.all()
    return [
        {
            "id": repo.id,
            "name": repo.name,
            "url": repo.url,
            "last_retrieved": repo.last_retrieved,
        }
        for repo in repos
    ]
