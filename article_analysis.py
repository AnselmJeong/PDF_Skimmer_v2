from typing import Literal

from config import CONFIG
from utils import get_file_url

from chatbot import Chatbot

BASE_URL = CONFIG["directories"]["base_url"]
BASE_DIR = CONFIG["directories"]["base_dir"]


class ArticleAnalyzer:
    def __init__(self, provider: Literal["gemini", "openai"] = "gemini"):
        self.chatbot = Chatbot(type="analysis", provider=provider)

    def summarize(self, file_path: str) -> dict:
        url = get_file_url(file_path, base_url=BASE_URL)
        # print(f"URL: {url}")
        self.chatbot.set_url(url)

        try:
            response = self.chatbot.query_llm()
            # print("Response from the LLM:\n")
            # print(response)
            return response

        except Exception as e:
            print(f"Error generating summary: {e}")
            return None
