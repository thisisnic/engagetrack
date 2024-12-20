from flask import request, jsonify, render_template, redirect, url_for, flash
from app import app, db
from app.models import Repo, save_repo, delete_repo, fetch_all_repos
from app.fetcher import fetch_metrics
import requests
import asyncio
from datetime import datetime

BASE_API_URL = "http://127.0.0.1:5000"


@app.route("/repos", methods=["POST"])
def add_repo():
    """
    Add a GitHub repository to the database by its URL.

    Returns:
        JSON response indicating success or failure.
        HTTP Status Codes:
            201: Repository successfully added.
            400: Invalid request or missing URL.
            500: Unexpected error during processing.
    """
    data = request.get_json()
    repo_url = data.get("repo_url")
    print(f"Received repo_url: {repo_url}")  # Debug log

    if not repo_url:
        return jsonify({"error": "Repository URL is required."}), 400

    try:
        repo = save_repo(repo_url)
        print(f"Repository saved: {repo}")  # Debug log
        return (
            jsonify({"message": f"Repository {repo.url} added!", "repo_id": repo.id}),
            201,
        )
    except ValueError as e:
        print(f"Validation error: {e}")  # Debug log
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Unexpected error: {e}")  # Debug log
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.route("/repos/<int:repo_id>", methods=["DELETE"])
def delete_repo_by_id(repo_id):
    """
    Delete a repository by its ID.

    Args:
        repo_id (int): The ID of the repository to delete.

    Returns:
        JSON response indicating success or failure.
        HTTP Status Codes:
            200: Repository successfully deleted.
            404: Repository not found.
    """
    repo = db.session.get(Repo, repo_id)
    if not repo:
        return jsonify({"error": "Repository not found."}), 404

    if delete_repo(repo_id):
        return jsonify({"message": f"Repository {repo_id} deleted successfully."}), 200
    return jsonify({"error": "Repository not found."}), 404


@app.route("/repos/<int:repo_id>/delete", methods=["POST"])
def delete_repo(repo_id):
    """
    Delete a repository via a POST request and redirect to the repository list page.

    Args:
        repo_id (int): The ID of the repository to delete.

    Returns:
        Redirect to the repository list page.
    """
    repo = db.session.get(Repo, repo_id)

    try:
        db.session.delete(repo)
        db.session.commit()
        flash(f"Repository {repo.name} deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while deleting the repository: {e}", "danger")

    return redirect(url_for("list_repos"))


@app.route("/metrics", methods=["GET"])
def get_metrics():
    """
    Fetch metrics for all repositories.

    Returns:
        JSON response with metrics data.
        HTTP Status Codes:
            200: Metrics successfully fetched.
    """
    repos = fetch_all_repos()
    repo_urls = [repo["url"] for repo in repos]

    metrics = asyncio.run(fetch_metrics(repo_urls))
    return jsonify(metrics), 200


@app.route("/")
def index():
    """
    Render the index page.

    Returns:
        HTML template for the index page.
    """
    return render_template("index.html")


@app.route("/track", methods=["GET", "POST"])
def track_repo():
    """
    Track a new GitHub repository and optionally display its metrics.

    Methods:
        GET: Render the tracking page.
        POST: Add a repository and fetch its metrics.

    Returns:
        HTML template for the tracking or results page.
    """
    if request.method == "POST":
        repo_url = request.form.get("repo_url")
        print(f"Received repo_url from form: {repo_url}")  # Debug log

        if not repo_url:
            flash("Repository URL is required!", "error")
            return redirect(url_for("track_repo"))

        try:
            response = requests.post(
                f"{BASE_API_URL}/repos", json={"repo_url": repo_url}
            )
            print(
                f"Response from /repos: {response.status_code} - {response.json()}"
            )  # Debug log

            if response.status_code == 201:
                flash("Repository added successfully!", "success")
                metrics_response = requests.get(f"{BASE_API_URL}/metrics")
                if metrics_response.status_code == 200:
                    metrics = metrics_response.json()
                    repo_metrics = next(
                        (m for m in metrics if m["repo_url"] == repo_url), None
                    )
                    if repo_metrics:
                        return render_template(
                            "results.html", repo_url=repo_url, metrics=[repo_metrics]
                        )
                    else:
                        flash("Metrics not found for the repository.", "warning")
                        return redirect(url_for("list_repos"))
                else:
                    flash("Failed to fetch metrics.", "danger")
            else:
                flash("Failed to add repository. Please check the URL.", "danger")
        except Exception as e:
            flash("An unexpected error occurred. Please try again later.", "danger")
            print(f"Error: {e}")

    return render_template("track.html")


@app.route("/repos/list", methods=["GET"])
def list_repos():
    """
    Display a list of all tracked repositories.

    Returns:
        HTML template with the list of repositories.
    """
    repos = Repo.query.all()
    return render_template("repo_list.html", repos=repos)


@app.route("/repos", methods=["GET"])
@app.route("/repos/<int:repo_id>/metrics", methods=["GET"])
def show_metrics(repo_id):
    """
    Show metrics for a specific repository by its ID.

    Args:
        repo_id (int): The ID of the repository.

    Returns:
        HTML template with the repository's metrics.
    """
    repo = Repo.query.get_or_404(repo_id)

    metrics_response = requests.get(f"{BASE_API_URL}/metrics")
    if metrics_response.status_code == 200:
        metrics = metrics_response.json()
        repo_metrics = next((m for m in metrics if m["repo_url"] == repo.url), None)

        if repo_metrics:
            return render_template(
                "results.html", repo_url=repo.url, metrics=[repo_metrics]
            )
        else:
            flash("No metrics found for this repository.", "warning")
            return redirect(url_for("list_repos"))
    else:
        flash("Failed to fetch metrics from the API.", "danger")
        return redirect(url_for("list_repos"))


@app.route("/repos/<int:repo_id>/refresh", methods=["POST"])
def refresh_metrics(repo_id):
    """
    Refresh metrics for a specific repository by its ID.

    Args:
        repo_id (int): The ID of the repository.

    Returns:
        Redirect to the repository list page.
    """
    repo = Repo.query.get_or_404(repo_id)

    try:
        metrics = asyncio.run(fetch_metrics([repo.url]))
        if metrics:
            repo.last_retrieved = datetime.utcnow()
            db.session.commit()
            flash(f"Metrics for {repo.name} refreshed successfully!", "success")
        else:
            flash(f"Failed to refresh metrics for {repo.name}.", "warning")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while refreshing metrics: {e}", "danger")

    return redirect(url_for("list_repos"))
