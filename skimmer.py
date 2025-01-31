from article_analysis import ArticleAnalyzer
from db_manager import DatabaseManager
from pathlib import Path
from typing import Literal


class PDFSkimmer:
    def __init__(self, provider: Literal["gemini", "openai"] = "gemini"):
        self.article_analyzer = ArticleAnalyzer(provider=provider)
        self.db_manager = DatabaseManager()
        self.current_article = None

    def load_or_summary(self, file_path: str):
        # Check if summary exists in database
        if summary := self.db_manager.get_summary(file_path):
            return summary
        elif paper_summary := self.article_analyzer.summarize(file_path):
            # Convert PaperSummary to dict and add file_path
            paper_summary["file_path"] = Path(file_path).name

            # Create DatabaseSummary from the dict
            self.db_manager.save_summary(paper_summary)
            return paper_summary
        return None
