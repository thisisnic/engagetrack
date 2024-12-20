import unittest
from unittest.mock import patch, MagicMock
from app import app, db
from app.models import Repo
from app.fetcher import fetch_metrics


class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        """
        Set up the test client and initialize the database for testing.
        """
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = app.test_client()

        # Create database schema
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """
        Clean up the database after each test.
        """
        with app.app_context():
            db.session.remove()
            db.drop_all()

    @patch("app.models.requests.get")
    def test_add_repo_success(self, mock_get):
        """
        Test adding a new repository successfully.
        """
        mock_get.return_value = MagicMock(status_code=200)

        response = self.client.post("/repos", json={"repo_url": "owner/repo"})

        self.assertEqual(response.status_code, 201)
        self.assertIn(
            b"Repository owner/repo added!", response.data
        )  # Update this if needed

    @patch("app.models.requests.get")
    def test_add_repo_invalid_url(self, mock_get):
        """
        Test adding a repository with an invalid URL.
        """
        mock_get.return_value = MagicMock(status_code=404)

        response = self.client.post("/repos", json={"repo_url": "invalid/repo"})

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Repository invalid/repo does not exist", response.data)

    def test_delete_repo_success(self):
        """
        Test deleting a repository successfully.
        """

        with app.app_context():
            repo = Repo(name="test-repo", url="owner/test-repo")
            db.session.add(repo)
            db.session.commit()

            repo = db.session.get(
                Repo, repo.id
            )  # Re-query to ensure it's still bound to the session

            response = self.client.delete(f"/repos/{repo.id}")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Repository 1 deleted successfully.", response.data)

    def test_delete_repo_not_found(self):
        """
        Test attempting to delete a repository that does not exist.
        """
        response = self.client.delete("/repos/999")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Repository not found.", response.data)

    @patch("app.fetcher.fetch_metrics")
    def test_get_metrics(self, mock_fetch_metrics):
        """
        Test fetching metrics for all repositories.
        """
        with app.app_context():
            repo = Repo(name="test-repo", url="owner/test-repo")
            db.session.add(repo)
            db.session.commit()

        mock_fetch_metrics.return_value = [
            {
                "repo_url": "owner/test-repo",
                "contributors": [{"login": "user1", "contributions": 5}],
            }
        ]

        response = self.client.get("/metrics")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"owner/test-repo", response.data)

    def test_list_repos(self):
        """
        Test listing all repositories.
        """
        with app.app_context():
            repo1 = Repo(name="repo1", url="owner/repo1")
            repo2 = Repo(name="repo2", url="owner/repo2")
            db.session.add(repo1)
            db.session.add(repo2)
            db.session.commit()

        response = self.client.get("/repos/list")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"repo1", response.data)
        self.assertIn(b"repo2", response.data)

    @patch("app.fetcher.fetch_metrics")
    def test_refresh_metrics(self, mock_fetch_metrics):
        """
        Test refreshing metrics for a specific repository.
        """
        with app.app_context():
            repo = Repo(name="test-repo", url="owner/test-repo")
            db.session.add(repo)
            db.session.commit()

            repo = db.session.get(Repo, repo.id)

            # Refresh repo instance
            mock_fetch_metrics.return_value = [
                {
                    "repo_url": "owner/test-repo",
                    "contributors": [{"login": "user1", "contributions": 10}],
                }
            ]

            response = self.client.post(f"/repos/{repo.id}/refresh")
            self.assertEqual(response.status_code, 302)  # Redirect to /repos/list


if __name__ == "__main__":
    unittest.main()
