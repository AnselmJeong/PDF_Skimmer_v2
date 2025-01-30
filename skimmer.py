from pathlib import Path
from pdf_process import PDFProcessor
from db_manager import DatabaseManager
from config import CONFIG

share_codes = CONFIG["directories"]["share_codes"]


class PDFSkimmer:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.db_manager = DatabaseManager()
        self.current_pdf = None

    def list_pdfs(self, directory):
        pdf_files = []
        try:
            # Convert directory to Path object and recursively search for PDFs
            path = Path(directory)
            for pdf_path in path.rglob("*.pdf"):
                pdf_files.append(pdf_path)
        except Exception as e:
            print(f"Error listing PDFs: {e}")
        return pdf_files  # list of Path

    def load_pdf(self, file_path, directory):
        if isinstance(file_path, str):
            file_path = Path(file_path)
        self.current_pdf = directory / file_path
        self.share_code = share_codes.get(directory, None)
        if not self.share_code:
            raise ValueError(f"Share code not found for directory: {directory}")

        # Check if file_path is absolute or just the
        print(f"Loading PDF: {self.current_pdf.name}")

        # Check if summary exists in database
        cached_summary = self.db_manager.get_summary(file_path.name)
        if cached_summary:
            return {
                "file_path": file_path,
                "core_question": cached_summary["core_question"],
                "introduction": cached_summary["introduction"],
                "methodology": cached_summary["methodology"],
                "results": cached_summary["results"],
                "discussion": cached_summary["discussion"],
                "limitations": cached_summary["limitations"],
            }

        # Generate new summary
        if summary := self.pdf_processor.get_summary(self.current_pdf, self.share_code):
            # print(f"Summary type: {type(summary)}")
            self.db_manager.save_summary(self.current_pdf, summary)
            summary["file_path"] = self.current_pdf
            return summary
        return None


