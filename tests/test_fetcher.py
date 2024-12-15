import unittest
import asyncio
from app.fetcher import fetch_contributors, fetch_issues

class FetcherTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_contributors(self):
        repo_url = 'octocat/Hello-World'
        contributors = await fetch_contributors(repo_url)
        self.assertIsInstance(contributors, list)
        if contributors:
            self.assertIn('login', contributors[0])

    async def test_fetch_issues(self):
        repo_url = 'octocat/Hello-World'
        issues = await fetch_issues(repo_url)
        self.assertIsInstance(issues, list)
        if issues:
            self.assertIn('title', issues[0])

if __name__ == '__main__':
    unittest.main()
