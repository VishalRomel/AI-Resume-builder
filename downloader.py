import os
import requests


def download_file(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            file.write(response.content)
        print(f"Downloaded {url} to {save_path}")
    else:
        print(f"Failed to download {url}: {response.status_code}")


def download_files_from_text_file(text_file_path, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Open and read lines from the text file
    with open(text_file_path, "r") as file:
        lines = file.readlines()

    project_name = None

    # Loop through lines to process name and link pairs
    for line in lines:
        line = line.strip()

        if line.startswith("http"):  # This line is a download link
            if project_name:
                # Construct a save path using the project name
                file_extension = line.split("/")[
                    -1
                ]  # e.g., "main.zip" or "gh-pages.zip"
                save_path = os.path.join(save_dir, f"{project_name}_{file_extension}")
                download_file(line, save_path)
                project_name = None  # Reset project name after downloading
        else:
            # This line is a project name, so store it for the next link
            project_name = line


# Specify the paths
text_file_path = "download_links.txt"
save_dir = "downloads"

# Run the downloader
download_files_from_text_file(text_file_path, save_dir)
