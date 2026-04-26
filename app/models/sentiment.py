from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class ReferenceItem(BaseModel):
    title: str
    url: str

# 1. Definimos el formato de la respuesta que queremos de la IA
class AIAnalysis(BaseModel):
    ticker: str = Field(..., description="Símbolo de la criptomoneda analizada")
    score: int = Field(..., ge=0, le=100)
    sentiment: Literal["Bullish", "Bearish", "Neutral"]
    action_signal: Literal["BUY", "SELL", "HOLD"] = Field(
        default="HOLD", 
        description="Señal de trading algorítmica"
    )
    summary: str = Field(..., description="Resumen estricto de 3 líneas")

# 2. Lo enviamos al frontend con referencias, historia y el precio
class SentimentResponse(AIAnalysis):
    price_at_analysis: float = Field(
        default=0.0, 
        description="Precio del activo en el momento exacto del análisis"
    )
    references: List[ReferenceItem] = Field(default=[])
    history: List[int] = Field(default=[])