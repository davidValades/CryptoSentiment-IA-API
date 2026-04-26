import sqlite3
import logging
import os

logger = logging.getLogger(__name__)

class DatabaseClient:
    # 1. Obtenemos la ruta exacta de este archivo (db_client.py)
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Retrocedemos un nivel y creamos una carpeta dedicada llamada 'data'
    DATA_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "data")
    
    # 3. LA CLAVE: Forzamos al sistema operativo a crear la carpeta si no existe
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 4. Le damos a SQLite la ruta final dentro de esa carpeta que ya sabemos que existe
    DB_FILE = os.path.join(DATA_DIR, "oracle_memory.db")

    @classmethod
    def initialize_db(cls):
        try:
            with sqlite3.connect(cls.DB_FILE) as conn:
                cursor = conn.cursor()
                
                # 1. Tabla de la Billetera
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS wallet (
                        id INTEGER PRIMARY KEY CHECK (id = 1),
                        balance REAL NOT NULL DEFAULT 10000.0
                    )
                """)
                cursor.execute("INSERT OR IGNORE INTO wallet (id, balance) VALUES (1, 10000.0)")

                # 2. Tabla del Historial Unificada
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sentiment_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticker TEXT NOT NULL,
                        score INTEGER NOT NULL,
                        sentiment TEXT,
                        signal TEXT,
                        entry_price REAL,
                        tp_price REAL,
                        sl_price REAL,
                        close_price REAL,
                        pnl_pct REAL,
                        status TEXT DEFAULT 'OPEN',
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Error inicializando DB: {e}")

    # ==========================================
    # LÓGICA DE MEMORIA Y FEEDBACK LOOP
    # ==========================================
    
    @classmethod
    def get_trade_history_for_prompt(cls, ticker: str, current_price: float, limit: int = 5) -> str:
        """PUENTE DE MEMORIA: Compara predicciones pasadas con el precio actual."""
        try:
            with sqlite3.connect(cls.DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT signal, entry_price, status, pnl_pct, timestamp 
                       FROM sentiment_history 
                       WHERE ticker = ? AND signal != 'HOLD'
                       ORDER BY timestamp DESC LIMIT ?""", 
                    (ticker.upper(), limit)
                )
                rows = cursor.fetchall()
                
                if not rows:
                    return "No hay historial operativo previo para este activo."

                feedback_lines = []
                for signal, entry_price, status, pnl_pct, ts in rows:
                    if status == 'CLOSED':
                        # Operación ya cerrada por el vigilante
                        is_win = pnl_pct > 0
                        outcome = "ACIERTO ✅" if is_win else "ERROR ❌"
                        feedback_lines.append(
                            f"- En {ts}, recomendaste {signal} a ${entry_price:,.2f}. Operación CERRADA con {pnl_pct*100:+.2f}%. Resultado: {outcome}"
                        )
                    else:
                        # Operación abierta, calculamos PnL flotante
                        current_pnl = ((current_price - entry_price) / entry_price) if signal == "BUY" else ((entry_price - current_price) / entry_price)
                        is_win = current_pnl > 0
                        outcome = "GANANDO ✅" if is_win else "PERDIENDO ❌"
                        feedback_lines.append(
                            f"- En {ts}, recomendaste {signal} a ${entry_price:,.2f}. Operación ABIERTA. Precio actual: ${current_price:,.2f} ({current_pnl*100:+.2f}% flotante). Estado actual: {outcome}"
                        )
                
                return "\n".join(feedback_lines)
        except Exception as e:
            logger.error(f"Error generando feedback de rendimiento: {e}")
            return "Error al recuperar memoria de trading."

    @classmethod
    def get_history_scores(cls, ticker: str, limit: int = 5) -> list[int]:
        """Para el gráfico de puntos de la interfaz."""
        try:
            with sqlite3.connect(cls.DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT score FROM sentiment_history WHERE ticker = ? ORDER BY timestamp DESC LIMIT ?", 
                    (ticker.upper(), limit)
                )
                results = cursor.fetchall()
                scores = [r[0] for r in results]
                scores.reverse()
                return scores
        except Exception as e:
            logger.error(f"Error leyendo historial: {e}")
            return []

    # ==========================================
    # LÓGICA DE TRADING ENGINE Y WALLET
    # ==========================================

    @classmethod
    def save_analysis_and_trade(cls, ticker: str, score: int, sentiment: str, signal: str, price: float):
        """Guarda el análisis y establece TP/SL estáticos si es BUY/SELL."""
        tp_price = None
        sl_price = None
        status = 'CLOSED'

        if signal == "BUY":
            tp_price = price * 1.05
            sl_price = price * 0.98
            status = 'OPEN'
        elif signal == "SELL":
            tp_price = price * 0.95
            sl_price = price * 1.02
            status = 'OPEN'

        with sqlite3.connect(cls.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO sentiment_history 
                   (ticker, score, sentiment, signal, entry_price, tp_price, sl_price, status) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
                (ticker.upper(), score, sentiment, signal, price, tp_price, sl_price, status)
            )
            conn.commit()

    @classmethod
    def get_open_trades(cls):
        """Devuelve las operaciones abiertas para el Vigilante."""
        with sqlite3.connect(cls.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, ticker, signal, entry_price, tp_price, sl_price FROM sentiment_history WHERE status = 'OPEN'")
            return cursor.fetchall()

    @classmethod
    def close_trade(cls, trade_id: int, close_price: float, pnl_pct: float):
        """Cierra la operación y actualiza la billetera (basado en un bloque de $1000 por trade)."""
        with sqlite3.connect(cls.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE sentiment_history SET status = 'CLOSED', close_price = ?, pnl_pct = ? WHERE id = ?",
                (close_price, pnl_pct, trade_id)
            )
            pnl_usd = 1000 * pnl_pct
            cursor.execute("UPDATE wallet SET balance = balance + ? WHERE id = 1", (pnl_usd,))
            conn.commit()

    @classmethod
    def get_wallet_info(cls):
        """Obtiene datos para el panel lateral de la interfaz web."""
        with sqlite3.connect(cls.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM wallet WHERE id = 1")
            balance_row = cursor.fetchone()
            balance = balance_row[0] if balance_row else 10000.0
            
            # Traemos las últimas 10 operaciones que no sean HOLD
            cursor.execute("SELECT ticker, signal, entry_price, status, pnl_pct FROM sentiment_history WHERE signal != 'HOLD' ORDER BY id DESC LIMIT 10")
            trades = [{"ticker": r[0], "signal": r[1], "price": r[2] if r[2] else 0, "status": r[3], "pnl": r[4]} for r in cursor.fetchall()]
            
            return {"balance": balance, "recent_trades": trades}