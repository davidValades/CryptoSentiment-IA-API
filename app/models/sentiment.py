# app/models/sentiment.py
from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class ReferenceItem(BaseModel):
    title: str
    url: str

# --- MODELO PARA INGESTIÓN (NUEVO) ---
# Esto nos ayudará en el Paso 2 para mover datos entre servicios
class MarketDataIngest(BaseModel):
    price: float
    price_change_24h: float
    volume_24h: float
    rsi: Optional[float] = None
    headlines: List[dict] # Viene de CryptoPanic o RSS

# --- TUS MODELOS ORIGINALES (PERFECTOS) ---
class AIAnalysis(BaseModel):
    ticker: str = Field(..., description="Símbolo de la criptomoneda analizada")
    score: int = Field(..., ge=0, le=100)
    sentiment: Literal["Bullish", "Bearish", "Neutral"]
    action_signal: Literal["BUY", "SELL", "HOLD"] = Field(
        default="HOLD", 
        description="Señal de trading algorítmica"
    )
    summary: str = Field(..., description="Resumen estricto de 3 líneas")

class SentimentResponse(AIAnalysis):
    price_at_analysis: float = Field(
        default=0.0, 
        description="Precio del activo en el momento exacto del análisis"
    )
    references: List[ReferenceItem] = Field(default=[])
    history: List[int] = Field(default=[])