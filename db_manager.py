from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from config import CONFIG
from pathlib import Path
import os

from dotenv import load_dotenv
from typing import Optional
from custom_types import DatabaseSummary
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()

DB_NAME = CONFIG["database"]["db_name"]
BASE_DIR = CONFIG["directories"]["base_dir"]
Base = declarative_base()


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True)
    file_path = Column(String, unique=True)
    core_question = Column(Text)
    introduction = Column(Text)
    methodology = Column(Text)
    results = Column(Text)
    discussion = Column(Text)
    limitations = Column(Text)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def create_database_if_not_exists():
    # Get database URL and extract database name
    postgres_url = os.getenv("POSTGRES_URL") + "/" + "postgres"

    try:
        conn = psycopg2.connect(postgres_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"Database {DB_NAME} created successfully")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error creating database: {e}")
        raise


class DatabaseManager:
    def __init__(self):
        create_database_if_not_exists()
        postgres_url = os.getenv("POSTGRES_URL") + "/" + DB_NAME
        self.engine = create_engine(postgres_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def save_summary(self, summary_data: dict) -> None:
        file_path = summary_data.get("file_path")
        try:
            # Check if summary exists
            if summary := self.session.query(Summary).filter_by(file_path=file_path).first():
                pass
            else:
                summary = Summary()
                self.session.add(summary)

            # Convert Pydantic model to dictionary and update SQLAlchemy model
            for key, value in summary_data.items():
                setattr(summary, key, value)

            self.session.commit()

        except Exception as e:
            print(f"Error saving summary: {e}")
            self.session.rollback()
            raise

    def get_summary(self, file_path: str) -> dict:
        file_path = Path(file_path).name

        if summary := self.session.query(Summary).filter_by(file_path=file_path).first():
            summary_dict = {
                column.name: getattr(summary, column.name)
                for column in summary.__table__.columns
                if column.name not in ["id", "last_updated"]
            }

            return summary_dict
        else:
            print(f"No summary found for {file_path}")
            return None
