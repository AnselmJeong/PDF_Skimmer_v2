import urllib.parse
from pathlib import Path


def get_file_url(file_path: str | Path, base_url: str) -> str:
    if isinstance(file_path, str):
        file_path = Path(file_path)
    # URL encode the filename
    encoded_filename = urllib.parse.quote(str(file_path))

    # Combine base URL with encoded filename
    full_url = base_url + encoded_filename

    return full_url
