# 🔮 CryptoSentiment AI API (MVP 1.0)

API RESTful que actúa como un **Oráculo de Mercado**. Combina datos cuantitativos (Binance) y cualitativos (Noticias RSS) para generar un análisis de sentimiento mediante **Google Gemini 2.0 Flash**.

## 🚀 Características

- **Arquitectura Limpia**: Separación de responsabilidades (Servicios, Modelos, Rutas).
- **IA Multimodal**: Procesa texto y datos numéricos en un solo prompt.
- **Asíncrona**: Construida sobre FastAPI y HTTPX para máximo rendimiento.
- **Validación Estricta**: Pydantic v2 garantiza que la IA siempre responda en el formato correcto.

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python 3.12+
- **Framework:** FastAPI
- **IA:** Google GenAI SDK (Gemini 2.0 Flash)
- **Datos:** Binance API & RSS News Feeds

## 🔧 Instalación y Setup

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/davidValades/CryptoSentiment-IA-API.git](https://github.com/davidValades/CryptoSentiment-IA-API.git)
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
   Crea un archivo ".env" en la raíz con:
   ```bash
   GEMINI_API_KEY=tu_clave_de_google_ai_studio
   ```

## 📈 Uso

Inicia el servidor:

```bash
uvicorn main:app --reload
```

Accede a la documentación interactiva en: http://127.0.0.1:8000/docs
