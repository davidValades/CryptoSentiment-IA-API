from pydantic import BaseModel, Field
from typing import Literal, List

class ReferenceItem(BaseModel):
    title: str
    url: str

class SentimentResponse(BaseModel):
    ticker: str = Field(
        ..., 
        description="Símbolo de la criptomoneda analizada (ej. BTC)"
    )
    score: int = Field(
        ..., 
        ge=0, 
        le=100, 
        description="Puntuación de sentimiento: 0 (Miedo Extremo/Bearish) a 100 (Avaricia Extrema/Bullish)"
    )
    sentiment: Literal["Bullish", "Bearish", "Neutral"] = Field(
        ..., 
        description="Clasificación categórica del sentimiento del mercado"
    )
    summary: str = Field(
        ..., 
        description="Resumen estricto de 3 líneas justificando el análisis basado en precio, volumen y noticias"
    )
    references: List[ReferenceItem] = Field(
        default=[], 
        description="Noticias utilizadas como contexto con sus respectivos enlaces"
    )
    history: List[int] = Field(
        default=[], 
        description="Historial de scores de los últimos 5 análisis")

    model_config = {
        "json_schema_extra": {
            "example": {
                "ticker": "BTC",
                "score": 82,
                "sentiment": "Bullish",
                "summary": "1. El precio ha roto resistencias clave con un aumento del 15% en el volumen de 24h.\n2. Los titulares en CryptoPanic muestran una fuerte adopción institucional reciente.\n3. La confluencia de métricas on-chain indica un claro momentum alcista.",
                "references": [
                    {"title": "Bitcoin rompe la barrera de los 80K", "url": "https://cointelegraph.com/..."}
                ]
            }
        }
    }