import logging
from google import genai
from google.genai import types
from app.models.sentiment import SentimentResponse, ReferenceItem
from app.core.config import settings 

logger = logging.getLogger(__name__)

class SentimentAgent:

    @staticmethod
    async def analyze_market_data(
        ticker: str, 
        binance_data: dict, 
        rsi_value: float,       
        headlines: list[dict], 
        fng_data: dict,
        previous_score: int = None,
        api_key: str = None,
        model_name: str = settings.GEMINI_MODEL
    ) -> SentimentResponse:
        
        # 1. Instanciar el cliente "Al Vuelo" con la clave recibida o la de defecto
        final_api_key = api_key if api_key else settings.GEMINI_API_KEY
        client = genai.Client(api_key=final_api_key)

        # 2. EXTRACCIÓN DE DATOS CRUDOS
        price_raw = float(binance_data.get('last_price', 0))
        change_raw = float(binance_data.get('price_change_percent', 0))
        vol_usd = float(binance_data.get('volume_24h', 0))

        if price_raw < 1:
            price_str = f"{price_raw:.4f}"
        else:
            price_str = f"{price_raw:,.2f}"
            
        change_str = f"{change_raw:+.2f}%"
        vol_str = f"{vol_usd:,.0f}"
        
        linea_maestra = f"El activo cotiza a ${price_str} USD ({change_str}) con un volumen de 24h de ${vol_str} USD."

        # 4. IA - Análisis de Sentimiento con Gemini
        system_instruction = """
        Eres el Analista Cuantitativo Jefe de un fondo de cobertura (Hedge Fund) en Wall Street.
        
        REGLAS ESTRICTAS:
        1. RESPONDE ÚNICA Y ESTRICTAMENTE EN ESPAÑOL.
        2. Tu 'summary' DEBE tener EXACTAMENTE 3 líneas (separadas por \n) con un nivel de profundidad técnico extremo.
        3. NO menciones el precio, porcentaje de cambio o volumen actual.
        4. Analiza la divergencia entre el RSI técnico, el sentimiento Macro (Fear & Greed) y la narrativa institucional de las noticias.
        5. Usa jerga financiera avanzada.
        6. Sé directo, frío y calculador.
        """

        formatted_headlines = "\n".join([f"- {h['title']}" for h in headlines])
        
        memory_context = f"- Score Anterior (Ayer): {previous_score}/100. Analiza si la tendencia mejora o empeora." if previous_score else "- No hay datos previos de ayer."

        user_prompt = f"""
        Analiza el activo: {ticker.upper()}
        (Contexto: Hoy ha tenido un cambio de {change_str}).
        
        MÉTRICAS TÉCNICAS Y MACROECONÓMICAS:
        - Fear & Greed Index Global: {fng_data.get('value', '50')}/100 ({fng_data.get('classification', 'Neutral')})
        - RSI (14 días) del activo: {rsi_value}
        
        MEMORIA TEMPORAL:
        {memory_context}
        
        NARRATIVA INSTITUCIONAL:
        {formatted_headlines}
        """

        try:
            # El cliente de Gemini se encarga de serializar el prompt y validar la respuesta contra el esquema de SentimentResponse
            response = await client.aio.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.4, 
                    response_mime_type="application/json",
                    response_schema=SentimentResponse,
                ),
            )
            
            resultado_ia = SentimentResponse.model_validate_json(response.text)
            lineas_ia = [line for line in resultado_ia.summary.split('\n') if line.strip()]
            resultado_ia.summary = linea_maestra + "\n" + "\n".join(lineas_ia[:2])
            resultado_ia.references = [ReferenceItem(title=h['title'], url=h['url']) for h in headlines]
            
            return resultado_ia

        except Exception as e:
            logger.error(f"Error crítico en la IA para {ticker}: {e}")
            raise Exception(f"Fallo al procesar Gemini: {str(e)}")