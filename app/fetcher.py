import aiohttp
import asyncio
from datetime import datetime, timedelta
import os

GITHUB_TOKEN = os.getenv("GH_API_TOKEN")


async def fetch_contributors(repo_url):
    """
    Fetch the top contributors for a given GitHub repository in the last 3 months.

    Args:
        repo_url (str): The GitHub repository URL in the format "owner/repo".

    Returns:
        list[dict]: A list of dictionaries containing contributor login and contribution count.
        Example: [{"login": "user1", "contributions": 42}, ...]

    Raises:
        ValueError: If the GitHub API token is not set in the environment.
        Exception: For API errors or rate limit issues.
    """
    async with aiohttp.ClientSession() as session:
        try:
            if not GITHUB_TOKEN:
                raise ValueError(
                    "GitHub API token not found. Set GH_API_TOKEN in your environment."
                )

            # Calculate the date 3 months ago
            three_months_ago = datetime.now() - timedelta(days=90)
            three_months_ago_iso = three_months_ago.isoformat()

            # API URL for fetching commits
            url = f"https://api.github.com/repos/{repo_url}/commits?since={three_months_ago_iso}"
            headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

            # Make the API request
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    commits = await response.json()

                    # Count contributions per author
                    contributors = {}
                    for commit in commits:
                        author = commit.get("commit", {}).get("author", {}).get("name")
                        if author:
                            contributors[author] = contributors.get(author, 0) + 1

                    # Sort contributors by contributions and take the top 10
                    top_contributors = sorted(
                        contributors.items(), key=lambda x: x[1], reverse=True
                    )[:10]
                    return [
                        {"login": contributor[0], "contributions": contributor[1]}
                        for contributor in top_contributors
                    ]

                elif response.status == 403:
                    raise Exception(
                        "GitHub API rate limit exceeded. Ensure your token has sufficient quota."
                    )
                else:
                    raise Exception(f"GitHub API error: {response.status}")

        except Exception as e:
            print(f"Error fetching contributors for {repo_url}: {e}")
            return []


async def fetch_issues(repo_url):
    """
    Fetch open issues for a given GitHub repository.

    Args:
        repo_url (str): The GitHub repository URL in the format "owner/repo".

    Returns:
        list[dict]: A list of issues in JSON format if successful.
        dict: An error message dictionary if fetching issues fails.
    """
    async with aiohttp.ClientSession() as session:
        url = f"https://api.github.com/repos/{repo_url}/issues"
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return {"error": f"Failed to fetch issues for {repo_url}"}


async def fetch_metrics(repo_urls):
    """
    Fetch metrics for multiple repositories, including top contributors.

    Args:
        repo_urls (list[str]): A list of GitHub repository URLs in the format "owner/repo".

    Returns:
        list[dict]: A list of dictionaries containing the repository URL and its contributors.
        Example: [{"repo_url": "owner/repo", "contributors": [...]}, ...]
    """
    tasks = []
    for repo_url in repo_urls:
        tasks.append(fetch_contributors(repo_url))
    results = await asyncio.gather(*tasks)

    metrics = []
    for i, repo_url in enumerate(repo_urls):
        contributors = results[i]
        metrics.append({"repo_url": repo_url, "contributors": contributors})
    return metrics
