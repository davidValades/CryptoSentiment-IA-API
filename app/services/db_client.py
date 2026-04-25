import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseClient:
    DB_FILE = "oracle_memory.db"

    @classmethod
    def initialize_db(cls):
        """Crea la tabla si no existe."""
        try:
            with sqlite3.connect(cls.DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sentiment_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticker TEXT NOT NULL,
                        score INTEGER NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Error inicializando SQLite: {e}")

    @classmethod
    def save_score(cls, ticker: str, score: int):
        """Guarda un nuevo análisis en el historial."""
        try:
            with sqlite3.connect(cls.DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO sentiment_history (ticker, score) VALUES (?, ?)", 
                    (ticker.upper(), score)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error guardando score en SQLite: {e}")

    @classmethod
    def get_latest_score(cls, ticker: str) -> int:
        """Obtiene el último score registrado para un ticker. Devuelve None si no hay."""
        try:
            with sqlite3.connect(cls.DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT score FROM sentiment_history WHERE ticker = ? ORDER BY timestamp DESC LIMIT 1", 
                    (ticker.upper(),)
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Error leyendo SQLite: {e}")
            return None