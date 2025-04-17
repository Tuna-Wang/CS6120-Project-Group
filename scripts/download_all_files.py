import os
from google.cloud import storage

BUCKET_NAME = "final-project-2025-bucket"
KEY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../key.json"))
DOWNLOAD_DIR = "./downloads"

def download_all_files_from_bucket(bucket_name: str, destination_folder: str):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blobs = bucket.list_blobs()
    os.makedirs(destination_folder, exist_ok=True)

    downloaded_files = []

    print(f"📦 Starting download from GCS bucket: {bucket_name}")
    for blob in blobs:
        local_path = os.path.join(destination_folder, blob.name)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)
        print(f"✅ Downloaded: {blob.name} → {local_path}")
        downloaded_files.append(local_path)

    print(f"\n🎉 Finished! {len(downloaded_files)} file(s) downloaded.")
    return downloaded_files


if __name__ == "__main__":
    download_all_files_from_bucket(BUCKET_NAME, DOWNLOAD_DIR)
