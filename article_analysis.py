from typing import Literal
from pathlib import Path
import urllib.parse
from config import CONFIG

from custom_types import PaperSummary

from chatbot import Chatbot

BASE_URL = CONFIG["directories"]["base_url"]
BASE_DIR = CONFIG["directories"]["base_dir"]


def get_file_url(file_path: str | Path, base_url: str = BASE_URL) -> str:
    if isinstance(file_path, str):
        file_path = Path(file_path)
    # Remove the BASE_DIR part from the file_path
    if str(file_path).startswith(BASE_DIR):
        file_path = file_path.relative_to(BASE_DIR)
    # URL encode the filename
    encoded_filename = urllib.parse.quote(str(file_path.name))

    # Combine base URL with encoded filename
    full_url = "/".join([base_url, encoded_filename])

    return str(full_url)


class ArticleAnalyzer:
    def __init__(self, provider: Literal["gemini", "openai"] = "gemini"):
        self.chatbot = Chatbot(type="analysis", provider=provider)

    def summarize(self, file_path: str) -> dict:
        url = get_file_url(file_path, base_url=BASE_URL)
        print(f"URL: {url}")
        self.chatbot.set_url(url)

        try:
            response = self.chatbot.query_llm()
            print("Response from the LLM:\n")
            print(response)
            return response

        except Exception as e:
            print(f"Error generating summary: {e}")
            return None
