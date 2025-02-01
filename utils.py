import re
from pathlib import Path
import urllib.parse
from config import CONFIG

BASE_URL = CONFIG["directories"]["base_url"]
BASE_DIR = CONFIG["directories"]["base_dir"]


def get_file_url(file_path: str | Path, base_url: str = BASE_URL) -> str:
    if isinstance(file_path, str):
        file_path = Path(file_path)
    # Remove the BASE_DIR part from the file_path
    if str(file_path).startswith(BASE_DIR):
        file_path = file_path.relative_to(BASE_DIR)
    # URL encode the filename
    encoded_filename = urllib.parse.quote(str(file_path))

    # Combine base URL with encoded filename
    full_url = "/".join([base_url, encoded_filename])

    return str(full_url)


def paragraph_to_markdown_list(paragraph):
    # Split the paragraph into sentences using regex
    sentences = re.split(r"(?<=[.!?]) +", paragraph)

    # Convert each sentence into a Markdown list item
    markdown_list = "\n".join(f"* {sentence}" for sentence in sentences)

    return markdown_list
