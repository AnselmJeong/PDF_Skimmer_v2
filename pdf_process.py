import google.generativeai as genai

import os
import json
from dotenv import load_dotenv
from link_converter import convert_filename_to_link
from summary_types import PaperSummary
from typing import Optional
from config import CONFIG

load_dotenv()


class PDFProcessor:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            CONFIG["model"]["gemini_model_name"],
            system_instruction=CONFIG["prompts"]["paper_analysis"],
        )
        self.chat = None
        self.link = None

    def get_external_links(self, file_path: str, share_code: str) -> Optional[str]:
        try:
            self.link = convert_filename_to_link(file_path, share_code)
            print(f"Link: {self.link}")
            return self.link
        except Exception as e:
            print(f"Error getting external link: {e}")
            return None

    def get_summary(self, file_path: str, share_code: str) -> Optional[PaperSummary]:
        external_link = self.get_external_links(file_path, share_code)
        print(f"External link: {external_link}")
        if not external_link:
            return None

        try:
            response = self.model.generate_content(
                f"LINK: {external_link}",
                generation_config=genai.GenerationConfig(
                    temperature=0.7,
                    response_mime_type="application/json",
                    response_schema=PaperSummary,
                ),
            )
            output = json.loads(response.text)

            return PaperSummary(**output)

        except Exception as e:
            print(f"Error generating summary: {e}")
            return None