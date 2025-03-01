import unittest
from unittest.mock import patch, MagicMock
import mysql.connector
import os
import shutil
from Crypto.Cipher import AES
import hashlib
import pyotp

# Import the original modules
import database_setup as db
import register_window
import login_window
import file_upload
import file_download

# Constants for testing
TEST_DB_NAME = "test_secure_file_storage"
TEST_EMAIL = "test@example.com"
TEST_USERNAME = "testuser"
TEST_PASSWORD_HASH = "test_hash"
TEST_FILE_NAME = "test_file.txt"
TEST_FILE_CONTENT = b"This is a test file."

class TestSecureFileStorage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the test database and tables."""
        # Override the database name for testing
        db.DB_NAME = TEST_DB_NAME
        db.setup_database()

    @classmethod
    def tearDownClass(cls):
        """Clean up the test database after all tests."""
        conn = mysql.connector.connect(host=db.DB_HOST, user=db.DB_USER, password=db.DB_PASSWORD)
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE {TEST_DB_NAME}")
        cursor.close()
        conn.close()

    def setUp(self):
        """Set up test data before each test."""
        self.conn = mysql.connector.connect(host=db.DB_HOST, user=db.DB_USER, password=db.DB_PASSWORD, database=db.DB_NAME)
        self.cursor = self.conn.cursor()

        # Insert a test user
        self.cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                            (TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD_HASH))
        self.conn.commit()

    def tearDown(self):
        """Clean up test data after each test."""
        self.cursor.execute("DELETE FROM users WHERE email = %s", (TEST_EMAIL,))
        self.cursor.execute("DELETE FROM files WHERE filename LIKE %s", (f"%{TEST_FILE_NAME}%",))
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

        # Clean up any test files
        if os.path.exists("encrypted_files"):
            shutil.rmtree("encrypted_files")

    @patch('register_window.messagebox')
    @patch('register_window.root', MagicMock())
    def test_user_registration(self, mock_messagebox):
        """Test user registration."""
        # Mock the messagebox to avoid GUI popups
        mock_messagebox.showwarning = MagicMock()
        mock_messagebox.showerror = MagicMock()

        # Test valid registration
        register_window.register_user("newuser", "newuser@example.com")
        self.cursor.execute("SELECT id FROM users WHERE email = %s", ("newuser@example.com",))
        result = self.cursor.fetchone()
        self.assertIsNotNone(result, "User should be registered successfully.")

        # Test duplicate registration
        register_window.register_user("newuser", "newuser@example.com")
        mock_messagebox.showerror.assert_called_with("Error", "❌ User already exists! Please login instead.")

    @patch('login_window.messagebox')
    @patch('login_window.open_dashboard', MagicMock())
    def test_login_with_otp(self, mock_messagebox):
        """Test OTP-based login."""
        # Mock the messagebox to avoid GUI popups
        mock_messagebox.showinfo = MagicMock()
        mock_messagebox.showerror = MagicMock()

        # Generate and store OTP
        otp = login_window.generate_otp()
        login_window.store_otp(TEST_EMAIL, otp)

        # Verify correct OTP
        login_window.verify_otp(TEST_EMAIL, otp, MagicMock())
        mock_messagebox.showinfo.assert_called_with("Success", "✅ OTP Verified! Login Successful.")

        # Verify incorrect OTP
        login_window.verify_otp(TEST_EMAIL, "wrong_otp", MagicMock())
        mock_messagebox.showerror.assert_called_with("Error", "❌ Incorrect OTP. Try again.")

    @patch('file_upload.filedialog.askopenfilename')
    @patch('file_upload.messagebox')
    def test_file_upload(self, mock_messagebox, mock_askopenfilename):
        """Test file upload and encryption."""
        # Mock the file dialog and messagebox
        mock_askopenfilename.return_value = TEST_FILE_NAME
        mock_messagebox.showwarning = MagicMock()
        mock_messagebox.showinfo = MagicMock()

        # Create a test file
        with open(TEST_FILE_NAME, "wb") as f:
            f.write(TEST_FILE_CONTENT)

        # Upload the file
        file_upload.upload_file(TEST_EMAIL)

        # Check if the file was encrypted and stored in the database
        self.cursor.execute("SELECT file_path FROM files WHERE filename = %s", (f"{TEST_FILE_NAME}.enc",))
        result = self.cursor.fetchone()
        self.assertIsNotNone(result, "File should be uploaded and stored in the database.")

    @patch('file_download.filedialog.asksaveasfilename')
    @patch('file_download.messagebox')
    def test_file_download(self, mock_messagebox, mock_asksaveasfilename):
        """Test file download."""
        # Mock the file dialog and messagebox
        mock_asksaveasfilename.return_value = "downloaded_file.txt"
        mock_messagebox.showinfo = MagicMock()

        # Create a test file and upload it
        with open(TEST_FILE_NAME, "wb") as f:
            f.write(TEST_FILE_CONTENT)
        file_upload.upload_file(TEST_EMAIL)

        # Download the file
        file_download.download_file(TEST_EMAIL)

        # Verify the downloaded file
        self.assertTrue(os.path.exists("downloaded_file.txt"), "File should be downloaded successfully.")

if __name__ == "__main__":
    unittest.main()