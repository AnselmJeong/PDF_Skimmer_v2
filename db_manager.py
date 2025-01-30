from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import os
from pathlib import Path
from dotenv import load_dotenv
import tomli
from typing import Optional
from summary_types import PaperSummary, DatabaseSummary
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()


def load_config():
    with open("config.toml", "rb") as f:
        return tomli.load(f)


CONFIG = load_config()

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
    db_url = os.getenv("postgresql_url")
    db_name = db_url.split("/")[-1]

    # Create connection string to postgres database
    postgres_url = "/".join(db_url.split("/")[:-1]) + "/postgres"

    try:
        # Connect to postgres database
        conn = psycopg2.connect(postgres_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database {db_name} created successfully")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error creating database: {e}")
        raise


class DatabaseManager:
    def __init__(self):
        create_database_if_not_exists()
        db_url = os.getenv("postgresql_url")
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def save_summary(self, file_path: str, summary_data: PaperSummary) -> None:
        file_name = Path(file_path).name
        try:
            # Check if summary exists
            summary = self.session.query(Summary).filter_by(file_path=file_name).first()

            if not summary:
                summary = Summary(file_path=file_name)
                self.session.add(summary)

            # Save each field directly
            # summary_data is a PaperSummary object passed as a parameter to save_summary()
            # It contains the structured paper analysis data matching the fields defined in config.toml
            summary.core_question = summary_data.get("core_question")
            summary.introduction = summary_data.get("introduction")
            summary.methodology = summary_data.get("methodology")
            summary.results = summary_data.get("results")
            summary.discussion = summary_data.get("discussion")
            summary.limitations = summary_data.get("limitations")

            self.session.commit()

        except Exception as e:
            print(f"Error saving summary: {e}")
            self.session.rollback()
            raise

    def get_summary(self, file_path: str) -> Optional[DatabaseSummary]:
        summary = self.session.query(Summary).filter_by(file_path=file_path).first()
        if summary:
            package = DatabaseSummary(
                file_path=summary.file_path,
                core_question=summary.core_question,
                introduction=summary.introduction,
                methodology=summary.methodology,
                results=summary.results,
                discussion=summary.discussion,
                limitations=summary.limitations,
                last_updated=summary.last_updated,
            )
            # print(f"data read from db:\n {package}")
            return package
        return None
