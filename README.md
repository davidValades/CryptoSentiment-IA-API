# 🔮 CryptoSentiment AI Oracle (v2.0)

API RESTful y Dashboard interactivo que actúa como un **Oráculo de Mercado de grado institucional**. Combina análisis técnico (RSI), datos macroeconómicos (Fear & Greed Index) y análisis de narrativas (Noticias RSS) procesados por Inteligencia Artificial (**Google Gemini, OpenAI o Anthropic**).

## 🚀 Características Premium

- **Análisis Híbrido (Quant + Qual):** Cruza datos de precios y volumen de Binance con indicadores técnicos (RSI 14d) y sentimiento de noticias en tiempo real.
- **Memoria Temporal (SQLite):** El sistema recuerda análisis previos para detectar cambios de tendencia y divergencias.
- **Trazabilidad Total:** Cada veredicto de la IA incluye enlaces directos a las fuentes originales para auditoría del usuario.
- **BYOK Multi-Modelo (Plug & Play):** Soporte nativo para ChatGPT, Claude y Gemini. Trae tu propia API Key y configúrala directamente desde la interfaz web. ¡Cero configuración en el servidor!
- **Dashboard Profesional:** Interfaz oscura con notificaciones integradas, gráficos interactivos de TradingView e historial de tendencia visual.

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.12+, FastAPI, HTTPX.
- **IA:** Google GenAI, OpenAI SDK, Anthropic SDK.
- **Base de Datos:** SQLite3 (Persistencia de historial) y JSON (Fuentes RSS).
- **Frontend:** Tailwind CSS, JavaScript (Vanilla), TradingView Widgets.
- **Datos:** Binance API, Alternative.me (F&G), y múltiples feeds RSS institucionales.

---

## 🐳 Despliegue con Docker (Recomendado - Zero Config)

Hemos diseñado el sistema para que tenga un arranque **"Zero Config"**. No necesitas configurar variables de entorno ni tocar código.

### Requisitos previos:

- Tener instalado [Docker](https://www.docker.com/) y Docker Compose.

### Pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/davidValades/CryptoSentiment-IA-API.git
   cd CryptoSentiment-IA-API
   ```
2. **Construir y levantar el contenedor:**
   ```bash
   docker-compose up --build -d
   ```
3. **Configuración:**

   Abre tu navegador en `http://localhost:8000/`. El asistente de bienvenida automático te pedirá que introduzcas tu API Key y selecciones tu modelo preferido para empezar a operar.

Nota: La base de datos SQLite y las configuraciones RSS persisten gracias a los volúmenes de Docker. No perderás tus datos aunque reinicies el contenedor.

Comandos útiles de Docker:

- Ver los logs en tiempo real: docker-compose logs -f

- Detener el servidor: docker-compose down

---

## 🔧 Instalación Manual (Local)

Si prefieres no usar Docker y ejecutarlo directamente en tu máquina:

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
4. **Iniciar el servidor:**
   ```bash
   uvicorn main:app --reload
   ```
   Accede en: `http://127.0.0.1:8000/` y sigue el asistente de bienvenida automático.

---

## ⚙️ Panel de Control SaaS

Desde el icono de engranaje (⚙️) en el Dashboard puedes gestionar tu propio ecosistema de análisis sin tocar el código:

- Ajustar el Cerebro: Cambia entre Gemini, GPT-4o o Claude al instante. Las credenciales se guardan de forma segura y local en tu navegador (`localStorage`). El servidor nunca almacena tus claves privadas.

- Gestión de Modelos: El campo de modelo es libre; puedes escribir cualquier modelo compatible con las librerías oficiales (ej. `gpt-3.5-turbo`, `gemini-2.0-flash`, `claude-3-opus-20240229`).

- Fuentes de Noticias (RSS): Añade o elimina canales de noticias institucionales en tiempo real. La lista se guarda en el servidor (`sources.json`) y es persistente para todos tus análisis futuros.
