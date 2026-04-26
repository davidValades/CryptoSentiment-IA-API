import logging
import json
from google import genai
from google.genai import types
from app.models.sentiment import SentimentResponse, ReferenceItem, AIAnalysis
from app.core.config import settings 

# Nuevas librerías
import openai
import anthropic

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
        
        # 1. EXTRACCIÓN DE DATOS CRUDOS
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

        # 2. INSTRUCCIONES ESTRICTAS (Adaptadas para Multi-Modelo)
        system_instruction = """
        Eres el Analista Cuantitativo Jefe de un fondo de cobertura (Hedge Fund) en Wall Street.
        
        REGLAS ESTRICTAS:
        1. RESPONDE ÚNICA Y ESTRICTAMENTE EN ESPAÑOL.
        2. Tu 'summary' DEBE tener EXACTAMENTE 3 líneas (separadas por \n) con un nivel de profundidad técnico extremo.
        3. NO menciones el precio, porcentaje de cambio o volumen actual.
        4. Analiza la divergencia entre el RSI técnico, el sentimiento Macro y las noticias.
        5. Sé directo, frío y calculador.
        6. IMPORTANTE: DEBES RESPONDER ÚNICAMENTE CON UN JSON VÁLIDO QUE CUMPLA ESTE ESQUEMA:
        {
          "ticker": "SIMBOLO",
          "score": 85,
          "sentiment": "Bullish",
          "summary": "Línea 1.\\nLínea 2.\\nLínea 3."
        }
        NO incluyas texto fuera del JSON, ni bloques de código markdown.
        """

        formatted_headlines = "\n".join([f"- {h['title']}" for h in headlines])
        memory_context = f"- Score Anterior (Ayer): {previous_score}/100. Analiza si la tendencia mejora o empeora." if previous_score else "- No hay datos previos de ayer."

        user_prompt = f"""
        Analiza el activo: {ticker.upper()}
        (Contexto: Hoy ha tenido un cambio de {change_str}).
        
        MÉTRICAS TÉCNICAS Y MACROECONÓMICAS:
        - Fear & Greed Index Global: {fng_data.get('value', '50')}/100
        - RSI (14 días) del activo: {rsi_value}
        
        MEMORIA TEMPORAL:
        {memory_context}
        
        NARRATIVA INSTITUCIONAL:
        {formatted_headlines}
        """

        try:
            raw_json_response = ""
            
            # Asegurarnos de que el modelo esté en minúsculas para evaluarlo
            model_lower = model_name.lower().strip()

            # EL ENRUTADOR DE INTELIGENCIA ARTIFICIAL
            
            # --- RUTA 1: OPENAI (ChatGPT) ---
            if model_lower.startswith("gpt"):
                logger.info(f"Enrutando hacia OpenAI ({model_name})...")
                client_oai = openai.AsyncOpenAI(api_key=api_key)
                response = await client_oai.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0.4
                )
                raw_json_response = response.choices[0].message.content

            # --- RUTA 2: ANTHROPIC (Claude) ---
            elif model_lower.startswith("claude"):
                logger.info(f"Enrutando hacia Anthropic ({model_name})...")
                client_anth = anthropic.AsyncAnthropic(api_key=api_key)
                response = await client_anth.messages.create(
                    model=model_name,
                    max_tokens=1024,
                    system=system_instruction,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.4
                )
                raw_json_response = response.content[0].text

            # --- RUTA 3: GOOGLE GEMINI (Default) ---
            else:
                logger.info(f"Enrutando hacia Google Gemini ({model_name})...")
                final_api_key = api_key if api_key else settings.GEMINI_API_KEY
                if not final_api_key:
                    raise ValueError("No se proporcionó API Key para Gemini. Configúrala en el panel ⚙️.")
                    
                client_gemini = genai.Client(api_key=final_api_key)
                response = await client_gemini.aio.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.4, 
                        response_mime_type="application/json",
                        # ---> ¡CAMBIO CLAVE AQUÍ! Usamos el modelo plano <---
                        response_schema=AIAnalysis, 
                    ),
                )
                raw_json_response = response.text

            # ==========================================
            # PROCESAMIENTO COMÚN (El Interceptor)
            # ==========================================
            
            raw_json_response = raw_json_response.replace("```json", "").replace("```", "").strip()

            # Validamos con el modelo PLANO
            resultado_ia_plano = AIAnalysis.model_validate_json(raw_json_response)
            
            # Formateamos el texto
            lineas_ia = [line for line in resultado_ia_plano.summary.split('\n') if line.strip()]
            resumen_final = linea_maestra + "\n" + "\n".join(lineas_ia[:2])
            
            # ---> ¡NUEVO! Construimos la respuesta completa para el Frontend <---
            resultado_final = SentimentResponse(
                ticker=resultado_ia_plano.ticker,
                score=resultado_ia_plano.score,
                sentiment=resultado_ia_plano.sentiment,
                summary=resumen_final,
                references=[ReferenceItem(title=h['title'], url=h['url']) for h in headlines]
            )
            
            return resultado_final

        except Exception as e:
            logger.error(f"Error crítico en la IA ({model_name}) para {ticker}: {e}")
            raise Exception(f"Fallo al procesar el modelo '{model_name}': Verifica que tu API Key sea correcta. Detalle: {str(e)}")