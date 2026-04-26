from pydantic import BaseModel, Field
from typing import Literal, List

class ReferenceItem(BaseModel):
    title: str
    url: str

# 1. Definimos el formato de la respuesta que queremos de la IA
class AIAnalysis(BaseModel):
    ticker: str = Field(..., description="Símbolo de la criptomoneda analizada")
    score: int = Field(..., ge=0, le=100)
    sentiment: Literal["Bullish", "Bearish", "Neutral"]
    summary: str = Field(..., description="Resumen estricto de 3 líneas")

# 2. Lo enviamos al frontend con referencias y nuestra línea maestra
class SentimentResponse(AIAnalysis):
    references: List[ReferenceItem] = Field(default=[])
    history: List[int] = Field(default=[])