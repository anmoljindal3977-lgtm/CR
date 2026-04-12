"""
Utility module for downloading datasets from Google Drive.
"""

import os
from pathlib import Path


def ensure_data_available(data_dir="data"):
    """
    Ensure application_train.csv and application_test.csv are available.
    Downloads from Google Drive if not found locally.
    
    Args:
        data_dir (str): Directory to store datasets
    
    Raises:
        FileNotFoundError: If download fails or files are not available after download
    """
    train_path = os.path.join(data_dir, "application_train.csv")
    test_path = os.path.join(data_dir, "application_test.csv")
    
    # Check if files already exist
    if os.path.exists(train_path) and os.path.exists(test_path):
        print(f" Dataset already exists at {data_dir}/")
        return
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    # Download from Google Drive
    print("Downloading dataset from Google Drive...")
    try:
        import gdown
    except ImportError:
        raise ImportError(
            "gdown is required for downloading datasets. "
            "Install it with: pip install gdown"
        )
    
    drive_folder_url = "https://drive.google.com/drive/folders/1tNkmIAF7zFr_AXS494tyvp_GqfGdTESX?usp=sharing"

    # Google Drive file IDs for the application datasets
    # These correspond to files in the shared folder:
    # https://drive.google.com/drive/folders/1tNkmIAF7zFr_AXS494tyvp_GqfGdTESX?usp=sharing
    files_to_download = {
        "application_train.csv": "1tNl4Cjrbu3D0nCHMzDiHFKp6nxzqVTWx",
        "application_test.csv": "1tNcF1aq2gYIXDJf7FbQ6YxJZVmN9cF8K"
    }

    for filename, file_id in files_to_download.items():
        output_path = os.path.join(data_dir, filename)

        if os.path.exists(output_path):
            print(f" {filename} already downloaded")
            continue

        try:
            url = f"https://drive.google.com/uc?id={file_id}"
            print(f"Downloading {filename}...")
            gdown.download(url, output_path, quiet=False)
            print(f" {filename} downloaded successfully")
        except Exception as e:
            print(
                f"Failed to download {filename} from Google Drive by file ID: {str(e)}\n"
                f"Falling back to folder download for {drive_folder_url}"
            )

    missing_files = [
        filename
        for filename in files_to_download.keys()
        if not os.path.exists(os.path.join(data_dir, filename))
    ]

    if missing_files:
        print(
            "Some files were not downloaded by direct file ID. "
            "Attempting fallback download from the shared folder..."
        )
        try:
            gdown.download_folder(drive_folder_url, output=data_dir, quiet=False, use_cookies=False)
        except Exception as e:
            raise RuntimeError(
                f"Failed to download dataset folder from Google Drive: {str(e)}\n"
                f"Please ensure the folder URL is correct and accessible."
            )

        missing_files = [
            filename
            for filename in files_to_download.keys()
            if not os.path.exists(os.path.join(data_dir, filename))
        ]

        if missing_files:
            raise FileNotFoundError(
                f"Dataset files not found after folder fallback download: {', '.join(missing_files)}"
            )

    # Verify all files exist
    for filename in files_to_download.keys():
        output_path = os.path.join(data_dir, filename)
        if not os.path.exists(output_path):
            raise FileNotFoundError(
                f"Dataset {filename} not found at {output_path} after download attempt"
            )
    
    print(f" All datasets ready in {data_dir}/")


if __name__ == "__main__":
    ensure_data_available()
