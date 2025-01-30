from typing import TypedDict
from datetime import datetime
import typing_extensions as typing


class PaperSummary(typing.TypedDict):
    core_question: str
    introduction: str
    methodology: str
    results: str
    discussion: str
    limitations: str


class DatabaseSummary(TypedDict):
    file_path: str
    core_question: str
    introduction: str
    methodology: str
    results: str
    discussion: str
    limitations: str
    last_updated: datetime
