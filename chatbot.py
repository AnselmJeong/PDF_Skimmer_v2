from typing import Literal
import urllib.parse
from dotenv import load_dotenv
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeekAI
from langchain_community.llms.tongyi import Tongyi

from config import CONFIG
from custom_types import PaperSummary

load_dotenv()

SYSTEM_MESSAGE = {
    "analysis": CONFIG["prompts"]["analysis"],
    "chatbot": CONFIG["prompts"]["chatbot"],
}

MODEL_NAMES = {
    "gemini": CONFIG["model"]["gemini_model_name"],
    "openai": CONFIG["model"]["openai_model_name"],
    "deepseek": CONFIG["model"]["deepseek_model_name"],
    "qwen": CONFIG["model"]["qwen_model_name"],
}

PROVIDER_CLASSES = {
    "gemini": ChatGoogleGenerativeAI,
    "openai": ChatOpenAI,
    "deepseek": ChatDeepSeekAI,
    "qwen": Tongyi,
}

API_KEYS = {
    "gemini": os.getenv("GEMINI_API_KEY"),
    "openai": os.getenv("OPENAI_API_KEY"),
    "deepseek": os.getenv("DEEPSEEK_API_KEY"),
    "qwen": os.getenv("QWEN_API_KEY"),
}


class Chatbot:
    def __init__(
        self,
        type: Literal["analysis", "chatbot"],
        provider: Literal["gemini", "openai", "deepseek", "qwen"] = "gemini",
    ):
        """
        Create an instance of the Chatbot class, provide the file path, type of prompt, and provider.

        Parameters:
        -----------
        type : Literal["analysis", "chatbot"]
            The type of prompt to use. "analysis" for generating a structured report, "chatbot" for interactive Q&A.
        provider : Literal["gemini", "openai", "deepseek", "qwen"], optional
            The provider to use for the language model. Default is "gemini".

        """
        self.type = type
        self.provider = provider
        self.llm = PROVIDER_CLASSES[self.provider](
            model=MODEL_NAMES[self.provider],
            api_key=API_KEYS[self.provider],
        )
        if self.type == "analysis":
            self.llm = self.llm.with_structured_output(PaperSummary)
        self.url = None

    def set_url(self, url: str):
        """
        Parameters:
        -----------
        url : str
            The url of the article (from gradio.FileExplorer) for which the chatbot will generate a summary or chat.
        """
        parsed_url = urllib.parse.urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError(f"Invalid URL: {url}")
        else:
            self.url = url

    def _history_to_messages(self, history: list):
        """
        Because history comes from gradio.chatinterface, it has more keys than just role and content
        Therefore we need to filter out the extra keys to be compatible with langchain
        """
        return [{k: v for k, v in msg.items() if k in ["role", "content"]} for msg in history]

    def query_llm(self, query: str = "proceed", history: list = None) -> dict | str:
        """
        Query the language model.

        Parameters (Only used for the chatbot):
        -----------
        query : str
            The user's query to be sent to the language model.
        history : list
            The chat history which comes from gradio.chatinterface.

        Returns:
        --------
        str
            The response from the language model.
        """
        if self.url is None:
            raise ValueError("File path must be set by `set_url()` before querying the LLM")
        else:
            system_message = SYSTEM_MESSAGE[self.type].format(LINK=self.url)
            self.history_langchain = [{"role": "system", "content": system_message}]

        if self.type == "chatbot" and history is not None:
            self.history_langchain += self._history_to_messages(history)

        self.history_langchain.append({"role": "user", "content": query})

        # print(self.history_langchain)

        response = self.llm.invoke(self.history_langchain)

        # Handle different response types based on chat mode
        if self.type == "analysis":
            # For analysis mode, return the PaperSummary model as a dict
            return response.model_dump()
        else:
            # For chatbot mode, return the content
            return response.content
