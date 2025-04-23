import os
import unittest
import sys
# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.cloud_utils import download_all_files_from_bucket

# Set these before running the test
BUCKET_NAME = "final-project-2025-bucket"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(os.path.join(os.path.dirname(__file__), "../key.json"))
key_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
assert os.path.exists(key_path), f"❌ Key file not found: {key_path}"
SERVICE_ACCOUNT_KEY = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

class RealGCSDownloadTest(unittest.TestCase):

    def setUp(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_KEY
        self.download_dir = "./test_gcs_downloads"
        os.makedirs(self.download_dir, exist_ok=True)

    def test_real_download_from_gcs(self):
        downloaded_files = download_all_files_from_bucket(BUCKET_NAME, self.download_dir)

        self.assertGreater(len(downloaded_files), 0, "No files were downloaded from GCS.")
        for path in downloaded_files:
            self.assertTrue(os.path.isfile(path), f"Missing file: {path}")

    def tearDown(self):
        # Clean up downloaded files and directories
        for root, _, files in os.walk(self.download_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in os.listdir(root):
                full_path = os.path.join(root, name)
                if os.path.isdir(full_path):
                    os.rmdir(full_path)
        if os.path.exists(self.download_dir):
            os.rmdir(self.download_dir)

if __name__ == "__main__":
    unittest.main()
