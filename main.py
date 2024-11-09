import os
import zipfile

os.system("github.py")
os.system("downloader.py")

zip_dir = "downloads"  # Directory containing zip files
extract_dir = "extracted"  # Directory to extract contents

# Create extraction directory if it doesn't exist
if not os.path.exists(extract_dir):
    os.makedirs(extract_dir)

# Loop through all files in the zip_dir
print("extracting files")
for subdir, dirs, files in os.walk(zip_dir):
    for zipp in files:
        if zipp.endswith(".zip"):  # Ensure only zip files are processed
            filepath = os.path.join(subdir, zipp)
            with zipfile.ZipFile(filepath, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
                print(f"Extracted {zipp} to {extract_dir}")
