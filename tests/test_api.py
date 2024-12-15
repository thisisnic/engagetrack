import unittest
from app import app, db
from app.models import Repo

class APITestCase(unittest.TestCase):
    def setUp(self):
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()

        # Create the database and tables
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Drop the database tables
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_repo(self):
        response = self.client.post('/repos', json={'repo_url': 'octocat/Hello-World'})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('Repository Hello-World added!', data['message'])

    def test_list_repos(self):
        # Add a repository first
        self.client.post('/repos', json={'repo_url': 'octocat/Hello-World'})
        response = self.client.get('/repos')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Hello-World')

    def test_delete_repo(self):
        # Add a repository first
        add_response = self.client.post('/repos', json={'repo_url': 'octocat/Hello-World'})
        repo_id = add_response.get_json()['repo_id']
        # Delete the repository
        delete_response = self.client.delete(f'/repos/{repo_id}')
        self.assertEqual(delete_response.status_code, 200)
        # Confirm deletion
        list_response = self.client.get('/repos')
        data = list_response.get_json()
        self.assertEqual(len(data), 0)

    def test_get_metrics(self):
        # Add a repository first
        self.client.post('/repos', json={'repo_url': 'octocat/Hello-World'})
        response = self.client.get('/metrics')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)

if __name__ == '__main__':
    unittest.main()
