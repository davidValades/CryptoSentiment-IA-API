from pydantic import BaseModel, Field
from typing import Literal

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

    # Añadimos un ejemplo para que la auto-documentación de Swagger (Redoc/OpenAPI) quede impecable
    model_config = {
        "json_schema_extra": {
            "example": {
                "ticker": "BTC",
                "score": 82,
                "sentiment": "Bullish",
                "summary": "1. El precio ha roto resistencias clave con un aumento del 15% en el volumen de 24h.\n2. Los titulares en CryptoPanic muestran una fuerte adopción institucional reciente.\n3. La confluencia de métricas on-chain y sentimiento social indica un claro momentum alcista."
            }
        }
    }