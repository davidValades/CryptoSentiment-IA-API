import logging
from google import genai
from google.genai import types
from app.core.config import settings
from app.models.sentiment import SentimentResponse, ReferenceItem # <--- Importamos ReferenceItem

logger = logging.getLogger(__name__)
client = genai.Client(api_key=settings.GEMINI_API_KEY)

class SentimentAgent:

    @staticmethod
    async def analyze_market_data(
        ticker: str, 
        binance_data: dict, 
        rsi_value: float,       # <--- ¡AQUÍ ESTÁ LA PIEZA QUE FALTABA!
        headlines: list[dict], 
        fng_data: dict,
        previous_score: int | None
    ) -> SentimentResponse:
        
        # 1. EXTRACCIÓN DE DATOS CRUDOS
        price_raw = float(binance_data.get('last_price', 0))
        change_raw = float(binance_data.get('price_change_percent', 0))
        vol_usd = float(binance_data.get('volume_24h', 0))

        # 2. PYTHON HACE EL TRABAJO DURO
        if price_raw < 1:
            price_str = f"{price_raw:.4f}"
        else:
            price_str = f"{price_raw:,.2f}"
            
        change_str = f"{change_raw:+.2f}%"
        vol_str = f"{vol_usd:,.0f}"
        
        # LÍNEA MAESTRA MATEMÁTICA
        linea_maestra = f"El activo cotiza a ${price_str} USD ({change_str}) con un volumen de 24h de ${vol_str} USD."

        # 3. GEMINI HACE EL TRABAJO CREATIVO
        system_instruction = """
        Eres el Analista Cuantitativo Jefe de un fondo de cobertura (Hedge Fund) en Wall Street.
        
        REGLAS ESTRICTAS:
        1. RESPONDE ÚNICA Y ESTRICTAMENTE EN ESPAÑOL.
        2. Tu 'summary' DEBE tener EXACTAMENTE 3 líneas (separadas por \n) con un nivel de profundidad técnico extremo.
        3. NO menciones el precio, porcentaje de cambio o volumen actual (ya están cubiertos en la línea 1).
        4. Analiza la divergencia entre el RSI técnico, el sentimiento Macro (Fear & Greed) y la narrativa institucional de las noticias.
        5. Usa jerga financiera avanzada (ej. liquidez, order blocks, momentum, acumulación, risk-on/risk-off).
        6. Sé directo, frío y calculador.
        """

        formatted_headlines = "\n".join([f"- {h['title']}" for h in headlines])
        
        # Lógica para la memoria de ayer
        memory_context = f"- Score Anterior (Ayer): {previous_score}/100. Analiza si la tendencia está mejorando o empeorando respecto a este dato." if previous_score else "- No hay datos previos de ayer. Establece una línea base de sentimiento."

        user_prompt = f"""
        Analiza el activo: {ticker.upper()}
        (Contexto: Hoy ha tenido un cambio de {change_str}).
        
        MÉTRICAS TÉCNICAS Y MACROECONÓMICAS:
        - Fear & Greed Index Global: {fng_data.get('value', '50')}/100 ({fng_data.get('classification', 'Neutral')})
        - RSI (14 días) del activo: {rsi_value} (Recuerda: >70 es Sobrecomprado, <30 es Sobrevendido)
        
        MEMORIA TEMPORAL:
        {memory_context}
        
        NARRATIVA INSTITUCIONAL (Titulares recientes):
        {formatted_headlines}
        """

        try:
            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2, 
                    response_mime_type="application/json",
                    response_schema=SentimentResponse,
                ),
            )
            
            # 4. EL PATRÓN INTERCEPTOR
            resultado_ia = SentimentResponse.model_validate_json(response.text)
            
            lineas_ia = [line for line in resultado_ia.summary.split('\n') if line.strip()]
            resumen_final = linea_maestra + "\n" + "\n".join(lineas_ia[:2])
            resultado_ia.summary = resumen_final
            
            # INYECTAMOS LAS REFERENCIAS (Para que el Frontend pinte los links)
            resultado_ia.references = [ReferenceItem(title=h['title'], url=h['url']) for h in headlines]
            
            return resultado_ia

        except Exception as e:
            logger.error(f"Error crítico en la IA para {ticker}: {e}")
            raise Exception(f"Fallo al procesar Gemini: {str(e)}")