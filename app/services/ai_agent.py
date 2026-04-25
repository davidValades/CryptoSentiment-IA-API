import logging
from google import genai
from google.genai import types
from app.core.config import settings
from app.models.sentiment import SentimentResponse

logger = logging.getLogger(__name__)

# Instanciamos el cliente global usando la API Key de nuestra configuración
client = genai.Client(api_key=settings.GEMINI_API_KEY)

class SentimentAgent:
    
    @staticmethod
    async def analyze_market_data(
        ticker: str, 
        binance_data: dict, 
        headlines: list[str]
    ) -> SentimentResponse:
        """
        Envía los datos de mercado a Gemini y devuelve un análisis estructurado.
        """
        
        # System Prompt: Definimos el rol y las reglas inquebrantables
        system_instruction = """
        Eres un analista financiero cuantitativo y cualitativo experto en criptomonedas.
        Tu tarea es analizar los datos de precio/volumen y la confluencia con las noticias recientes para determinar el sentimiento del mercado.
        
        REGLAS ESTRICTAS:
        1. Eres un Oráculo automatizado. No incluyas saludos, despedidas ni texto markdown fuera del JSON.
        2. El 'summary' DEBE tener exactamente 3 líneas separadas por saltos de línea (\n).
        3. Sé objetivo y analítico. Justifica el 'score' basándote en la divergencia o convergencia entre el precio y las noticias.
        """

        # Formateamos los titulares en una lista legible
        formatted_headlines = "\n".join([f"- {h}" for h in headlines])

        # User Prompt: Inyectamos los datos dinámicos
        user_prompt = f"""
        Analiza el siguiente activo: {ticker.upper()}

        DATOS CUANTITATIVOS (Binance 24h):
        - Precio Actual: ${binance_data.get('last_price')}
        - Cambio 24h: {binance_data.get('price_change_percent')}%
        - Volumen 24h: {binance_data.get('volume_24h')}

        DATOS CUALITATIVOS (CryptoPanic Últimos Titulares):
        {formatted_headlines}
        """

        try:
            # Usamos el cliente asíncrono (.aio) para llamadas no bloqueantes
            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash', # Un modelo rápido y eficiente para análisis
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2, # Temperatura baja (0.2) para respuestas más analíticas y menos creativas
                    response_mime_type="application/json",
                    response_schema=SentimentResponse, # ¡La magia! Forzamos la salida al esquema de Pydantic
                ),
            )
            
            # Gemini nos devuelve un string JSON perfecto que validamos directamente con Pydantic
            return SentimentResponse.model_validate_json(response.text)

        except Exception as e:
            logger.error(f"Error crítico en la generación de IA para {ticker}: {e}")
            raise Exception(f"Fallo al procesar el análisis con Gemini: {str(e)}")