# 🔮 CryptoSentiment AI Oracle (v2.0)

API RESTful y Dashboard interactivo que actúa como un **Oráculo de Mercado de grado institucional**. Combina análisis técnico (RSI), datos macroeconómicos (Fear & Greed Index) y análisis de narrativas (Noticias RSS) procesados por **Google Gemini 3.1 Pro/Flash**.

## 🚀 Características

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

---

## 🐳 Despliegue con Docker (Recomendado)

La forma más rápida y segura de ejecutar el Oráculo es utilizando Docker. Esto garantiza que la aplicación funcione exactamente igual en cualquier máquina sin necesidad de configurar Python localmente.

### Requisitos previos:

- Tener instalado [Docker](https://www.docker.com/) y Docker Compose.

### Pasos:

1. **Clonar el repositorio:**

   ```bash
   git clone [https://github.com/davidValades/CryptoSentiment-IA-API.git](https://github.com/davidValades/CryptoSentiment-IA-API.git)
   cd CryptoSentiment-IA-API
   ```

2. **Configurar variables de entorno:**
   Crea un archivo llamado `.env` en la raíz del proyecto y añade tu clave de Google AI Studio (y opcionalmente el modelo por defecto):

   ```bash
   GEMINI_API_KEY=tu_clave_de_google_ai_studio
   GEMINI_MODEL=gemini-3.1-pro-preview
   ```

3. **Construir y levantar el contenedor:**
   Ejecuta el siguiente comando para iniciar la aplicación en segundo plano:

   ```bash
   docker-compose up --build -d
   ```

Ya puedes acceder al Dashboard abriendo tu navegador en: `http://localhost:8000/`

Nota: La base de datos SQLite y las configuraciones RSS persisten gracias a los volúmenes de Docker. No perderás tus datos aunque reinicies el contenedor.

- Comandos útiles de Docker:
- Ver los logs en tiempo real: docker-compose logs -f

Detener el servidor: docker-compose down

---

## 🔧 Instalación Manual (Local)

Si prefieres no usar Docker y ejecutarlo directamente en tu máquina:

1. Clonar el repositorio:

   ```bash
   git clone [https://github.com/davidValades/CryptoSentiment-IA-API.git](https://github.com/davidValades/CryptoSentiment-IA-API.git)
   cd CryptoSentiment-IA-API
   ```

2. Crear entorno virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:

   Crea el archivo `.env` igual que en el paso de Docker.

5. Iniciar el servidor:

   ```bash
   uvicorn main:app --reload
   ```

   Accede en:`http://127.0.0.1:8000/`

---

## ⚙️ Configuración Dinámica (Dashboard)

Desde el icono de engranaje (⚙️) en el Dashboard puedes:

- **Gestionar Fuentes:** Añadir o eliminar canales de noticias RSS en tiempo real.

- **Ajustar el Cerebro:** Cambiar la API Key y el modelo de IA sin necesidad de tocar el código ni reiniciar el servidor.

- **Persistencia:** Las claves de la IA se guardan de forma segura en el almacenamiento local de tu navegador (localStorage), mientras que la lista de fuentes RSS se guarda en el servidor.
