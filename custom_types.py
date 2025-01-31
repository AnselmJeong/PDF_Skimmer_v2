from pydantic import BaseModel


class PaperSummary(BaseModel):
    core_question: str
    introduction: str
    methodology: str
    results: str
    discussion: str
    limitations: str


class DatabaseSummary(BaseModel):
    file_path: str
    core_question: str
    introduction: str
    methodology: str
    results: str
    discussion: str
    limitations: str
