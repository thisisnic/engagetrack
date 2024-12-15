import unittest
from datetime import datetime
from app import app, db
from app.models import Repo

class APITestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_repo(self):
        response = self.client.post('/repos', json={'repo_url': 'octocat/Hello-World'})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('Repository Hello-World added!', data['message'])
        with app.app_context():
            repo = Repo.query.filter_by(url='octocat/Hello-World').first()
            self.assertIsNotNone(repo)
            self.assertEqual(repo.name, 'Hello-World')
            self.assertIsInstance(repo.last_retrieved, datetime)

    def test_list_repos(self):
        self.client.post('/repos', json={'repo_url': 'octocat/Hello-World'})
        response = self.client.get('/repos')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Hello-World')

    def test_delete_repo(self):
        add_response = self.client.post('/repos', json={'repo_url': 'octocat/Hello-World'})
        repo_id = add_response.get_json()['repo_id']
        delete_response = self.client.delete(f'/repos/{repo_id}')
        self.assertEqual(delete_response.status_code, 200)
        list_response = self.client.get('/repos')
        data = list_response.get_json()
        self.assertEqual(len(data), 0)

    def test_refresh_metrics(self):
        add_response = self.client.post('/repos', json={'repo_url': 'octocat/Hello-World'})
        repo_id = add_response.get_json()['repo_id']
        refresh_response = self.client.post(f'/repos/{repo_id}/refresh')
        self.assertEqual(refresh_response.status_code, 200)
        data = refresh_response.get_json()
        self.assertIn("Metrics refreshed", data['message'])

if __name__ == '__main__':
    unittest.main()
