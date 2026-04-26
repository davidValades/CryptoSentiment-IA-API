# 🔮 CryptoSentiment AI Oracle (v2.0)

API RESTful y Dashboard interactivo que actúa como un **Oráculo de Mercado de grado institucional**. Combina análisis técnico (RSI), datos macroeconómicos (Fear & Greed Index) y análisis de narrativas (Noticias RSS) procesados por **Google Gemini 3.1 Pro/Flash**.

## 🚀 Características Premium

- **Análisis Híbrido (Quant + Qual):** Cruza datos de precios y volumen de Binance con indicadores técnicos (RSI 14d) y sentimiento de noticias.
- **Memoria Temporal (SQLite):** El sistema recuerda análisis previos para detectar cambios de tendencia y divergencias.
- **Trazabilidad Total:** Cada veredicto de la IA incluye enlaces directos a las fuentes originales para auditoría del usuario.
- **BYOK (Bring Your Own Key):** Configuración dinámica desde la interfaz para usar tus propias API Keys y elegir cualquier modelo de Gemini (Flash o Pro).
- **Dashboard Profesional:** Interfaz oscura con gráficos dinámicos de TradingView e historial de tendencia visual.

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.12+, FastAPI, HTTPX.
- **IA:** Google GenAI SDK (Gemini 3.1 Pro/Flash).
- **Base de Datos:** SQLite3 (Persistencia de historial y fuentes).
- **Frontend:** Tailwind CSS, JavaScript (Vanilla), TradingView Widgets.
- **Datos:** Binance API, Alternative.me (F&G), y múltiples feeds RSS institucionales.

## 🔧 Instalación y Setup

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/davidValades/CryptoSentiment-IA-API.git
   cd CryptoSentiment-IA-API
   ```
2. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. **Instalar dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   Crea un archivo `.env` en la raíz con:
   ```bash
   GEMINI_API_KEY=tu_clave_de_google_ai_studio
   ```

## 📈 Uso

Inicia el servidor:

```bash
uvicorn main:app --reload
```

Accede a la interfaz en: `http://127.0.0.1:8000/`

## ⚙️ Configuración Dinámica

Desde el icono de engranaje (⚙️) en el Dashboard puedes:

- **Gestionar Fuentes:** Añadir o eliminar canales de noticias RSS en tiempo real.
- **Ajustar el Cerebro:** Cambiar la API Key y el modelo de IA sin reiniciar el servidor.

- **Persistencia:** Los cambios se guardan localmente en el navegador y en el servidor (sources.json).
