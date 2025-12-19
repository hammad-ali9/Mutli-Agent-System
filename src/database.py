import sqlite3
import json
from src.models import PredictionOutput, EventMetadata

class Database:
    def __init__(self, db_path: str = "predictions.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    rules TEXT,
                    resolution_date TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT,
                    agent_name TEXT,
                    prediction TEXT,
                    probability REAL,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES events (id)
                )
            """)

    def save_event(self, event: EventMetadata):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO events (id, title, description, rules, resolution_date) VALUES (?, ?, ?, ?, ?)",
                (event.event_id, event.title, event.description, event.resolution_rules, event.resolution_date)
            )

    def save_prediction(self, agent_name: str, prediction: PredictionOutput):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO predictions (event_id, agent_name, prediction, probability, data) VALUES (?, ?, ?, ?, ?)",
                (prediction.event_id, agent_name, prediction.prediction, prediction.probability, prediction.json())
            )
