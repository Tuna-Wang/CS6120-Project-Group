import os
from google.cloud import storage

def download_all_files_from_bucket(bucket_name: str, destination_folder: str = "./downloads"):
    """
    Downloads all objects from the specified GCS bucket into a local folder.
    
    Args:
        bucket_name (str): Name of the GCS bucket.
        destination_folder (str): Local folder to save the downloaded files.
    Returns:
        List of downloaded file paths.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blobs = bucket.list_blobs()
    os.makedirs(destination_folder, exist_ok=True)

    downloaded_files = []

    for blob in blobs:
        local_path = os.path.join(destination_folder, blob.name)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)
        downloaded_files.append(local_path)
        print(f"✅ Downloaded: {blob.name} -> {local_path}")

    return downloaded_files
