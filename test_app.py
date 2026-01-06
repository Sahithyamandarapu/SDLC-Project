import unittest
from app import app
import sqlite3

class TodoAppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_add_task(self):
        response = self.app.post('/add', data={
            'title': 'Test Task',
            'description': 'Testing phase',
            'priority': 'High'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Task', response.data)

if __name__ == "__main__":
    unittest.main()
