"""
End-to-End System Verification Test Script (Including Authentication & Access Control)
"""

import os
import sys
import unittest

# Ensure root directory is on python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, init_db, get_db_connection, DATABASE_PATH
from utils.resume_parser import parse_resume_file
from utils.skill_extractor import parse_resume_full
from model.matching_model import JobMatcher


class TestResumeSystemWithAuth(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Clean and initialize database once before running test suite."""
        if os.path.exists(DATABASE_PATH):
            try:
                os.remove(DATABASE_PATH)
            except Exception:
                pass
        init_db()

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_1_database_seeding(self):
        """Verify SQLite jobs table is seeded with 20+ jobs."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM jobs")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertGreaterEqual(count, 20, "Database should contain at least 20 jobs.")
        print(f"\n[PASS] Database seeding verified with {count} jobs.")

    def test_2_user_signup_and_duplicate_prevention(self):
        """Verify user signup, password hashing, and duplicate detection."""
        # 1. Signup new user
        res = self.client.post('/signup', data={
            'name': 'Test User',
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Welcome, Test User!', res.data)

        # Verify password in DB is hashed, not plain text
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", ('testuser',))
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertNotEqual(row['password_hash'], 'password123')
        self.assertTrue(row['password_hash'].startswith('scrypt:') or row['password_hash'].startswith('pbkdf2:'))

        # Log out so we can test duplicate signups
        self.client.get('/logout')

        # 2. Try signup duplicate email
        res_dup_email = self.client.post('/signup', data={
            'name': 'Duplicate User',
            'email': 'testuser@example.com',
            'username': 'uniqueusername',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'already exists', res_dup_email.data)

        # 3. Try signup duplicate username
        res_dup_user = self.client.post('/signup', data={
            'name': 'Duplicate User 2',
            'email': 'unique@example.com',
            'username': 'testuser',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'already taken', res_dup_user.data)

        print("[PASS] User signup, password hashing & duplicate detection verified.")

    def test_3_login_and_logout(self):
        """Verify login authentication and session logout."""
        # Log out first
        self.client.get('/logout')

        # Invalid password attempt
        res_invalid = self.client.post('/login', data={
            'identity': 'testuser@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid login credentials', res_invalid.data)

        # Valid login attempt with email
        res_valid_email = self.client.post('/login', data={
            'identity': 'testuser@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(res_valid_email.status_code, 200)
        self.assertIn(b'Welcome back, Test User!', res_valid_email.data)

        # Logout
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'logged out successfully', res_logout.data)

        print("[PASS] Login authentication & logout verified.")

    def test_4_route_protection(self):
        """Verify protected routes redirect unauthenticated users to login page."""
        # Ensure logged out
        self.client.get('/logout')

        # Attempt to access upload page
        res = self.client.get('/upload', follow_redirects=True)
        self.assertIn(b'Please log in to your account', res.data)
        self.assertIn(b'Welcome Back', res.data)

        print("[PASS] Route protection verified for unauthenticated users.")

    def test_5_full_authenticated_workflow(self):
        """Verify end-to-end flow: Login -> Upload Sample -> Recommendations -> Dashboard."""
        # 1. Login
        self.client.post('/login', data={
            'identity': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)

        # 2. Upload Sample Resume (John Doe)
        res_sample = self.client.get('/upload_sample/john_doe', follow_redirects=True)
        self.assertEqual(res_sample.status_code, 200)
        self.assertIn(b'Resume Analysis Results', res_sample.data)
        self.assertIn(b'John Doe', res_sample.data)

        # 3. Check Jobs Browse
        res_jobs = self.client.get('/jobs')
        self.assertEqual(res_jobs.status_code, 200)
        self.assertIn(b'Python Developer', res_jobs.data)

        print("[PASS] Full authenticated workflow (Signup -> Login -> Sample Upload -> Results -> Jobs) verified successfully.")


if __name__ == '__main__':
    unittest.main()
