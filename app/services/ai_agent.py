import re
import logging
from google import genai
from google.genai import types
from app.core.config import settings
from app.models.sentiment import SentimentResponse

logger = logging.getLogger(__name__)
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Elimina: "(-37%)", "( -37 %)", "-37%", "+1.5 %", "(37%)", etc.
_PCT_WITH_PARENS = re.compile(r"\(?\s*[+-]?\d+(?:[.,]\d+)?\s*%\s*\)?")

# Limpia artefactos tras el borrado: "()", "( )", espacios dobles
_EMPTY_PARENS   = re.compile(r"\(\s*\)")
_MULTI_SPACE    = re.compile(r" {2,}")

_MOVEMENT_PATTERN = re.compile(
    r"(?:(?:ligera?|fuerte|moderada?|leve|pequeña?|significativa?)\s+)?"
    r"(?:corrección|caída|baja|retroceso|subida|alza|avance|recuperación|repunte|descenso)"
    r"|consolidación|estancamiento|lateralización|movimiento\s+lateral",
    flags=re.IGNORECASE,
)


class SentimentAgent:

    @staticmethod
    async def analyze_market_data(
        ticker: str, 
        binance_data: dict, 
        headlines: list[str]
    ) -> SentimentResponse:
        
        # 1. EXTRACCIÓN DE DATOS CRUDOS
        price_raw = float(binance_data.get('last_price', 0))
        change_raw = float(binance_data.get('price_change_percent', 0))
        vol_usd = float(binance_data.get('volume_24h', 0))

        # 2. PYTHON HACE EL TRABAJO DURO (Determinista 100% preciso)
        # Si es una altcoin pequeña (ej. RON a 0.1009), mostramos 4 decimales. Si es BTC, usamos comas de miles y 2 decimales.
        if price_raw < 1:
            price_str = f"{price_raw:.4f}"
        else:
            price_str = f"{price_raw:,.2f}"
            
        change_str = f"{change_raw:+.2f}%"  # El '+' fuerza a poner + o - según corresponda
        vol_str = f"{vol_usd:,.0f}"         # Quitamos decimales al volumen para que se lea más limpio
        
        # ESTA SERÁ NUESTRA LÍNEA 1 INQUEBRANTABLE:
        linea_maestra = f"El activo cotiza a ${price_str} USD ({change_str}) con un volumen de 24h de ${vol_str} USD."

        # 3. GEMINI HACE EL TRABAJO CREATIVO (Probabilístico)
        system_instruction = """
        Eres un analista cualitativo de criptomonedas.
        
        REGLAS ESTRICTAS:
        1. RESPONDE ÚNICA Y ESTRICTAMENTE EN ESPAÑOL.
        2. Tu 'summary' DEBE tener EXACTAMENTE 2 líneas (separadas por un salto de línea \n).
        3. REGLA DE ORO: Tienes ABSOLUTAMENTE PROHIBIDO mencionar el precio, el porcentaje de cambio o el volumen. Yo me encargo de los números.
        4. Tu única tarea es justificar si el mercado está Bullish, Bearish o Neutral basándote exclusivamente en el contexto de las NOTICIAS proporcionadas.
        5. Eres un Oráculo automatizado.
        """

        formatted_headlines = "\n".join([f"- {h}" for h in headlines])

        user_prompt = f"""
        Analiza el activo: {ticker.upper()}
        (Contexto: El activo ha tenido un cambio de {change_str} hoy).
        
        TITULARES DE NOTICIAS RECIENTES:
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
            
            # 4. EL PATRÓN INTERCEPTOR (Ensamblamos el Frankenstein)
            resultado_ia = SentimentResponse.model_validate_json(response.text)
            
            # Limpiamos las líneas de la IA por si añade saltos de línea invisibles
            lineas_ia = [line for line in resultado_ia.summary.split('\n') if line.strip()]
            
            # Unimos nuestra línea matemática perfecta con las 2 líneas cualitativas de la IA
            resumen_final = linea_maestra + "\n" + "\n".join(lineas_ia[:2])
            
            # Sobrescribimos el resumen antes de devolverlo al Frontend
            resultado_ia.summary = resumen_final
            
            return resultado_ia

        except Exception as e:
            logger.error(f"Error crítico en la IA para {ticker}: {e}")
            raise Exception(f"Fallo al procesar Gemini: {str(e)}")


def _strip_and_inject(
    result: SentimentResponse,
    change_str: str,
    ticker: str,
) -> SentimentResponse:
    """
    Paso 1 — Elimina CUALQUIER porcentaje alucinado (con o sin paréntesis).
    Paso 2 — Inyecta el porcentaje real junto a la primera frase de movimiento.
    Paso 3 — Limpia artefactos residuales ("()", espacios dobles).
    """
    summary = getattr(result, "summary", "") or ""

    # --- Paso 1: borrado agresivo ---
    cleaned = _PCT_WITH_PARENS.sub("", summary)
    cleaned = _EMPTY_PARENS.sub("", cleaned)
    cleaned = _MULTI_SPACE.sub(" ", cleaned).strip()

    if cleaned != summary:
        logger.warning(f"[{ticker}] Porcentaje alucinado eliminado. Original: {summary!r}")

    # --- Paso 2: inyección del valor real ---
    injected, n = _MOVEMENT_PATTERN.subn(
        lambda m: f"{m.group(0)} ({change_str})",
        cleaned,
        count=1,
    )

    # --- Paso 3: fallback si no hubo match de frase ---
    if n == 0:
        lines = cleaned.split("\n")
        lines[0] = f"{lines[0]} ({change_str})"
        injected = "\n".join(lines)
        logger.warning(f"[{ticker}] Sin frase de movimiento; inyectado en línea 1.")

    result.summary = injected
    return result