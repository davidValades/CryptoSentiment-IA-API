# 🔮 CryptoSentiment AI API | Market Oracle

![Status](https://img.shields.io/badge/Estado-En_Desarrollo_🚀-2ea44f?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)

Una API RESTful de análisis cuantitativo y cualitativo que actúa como un "Oráculo" del mercado de criptomonedas. El sistema ingiere datos de mercado en tiempo real y titulares de noticias financieras para alimentar a un modelo de Inteligencia Artificial (Google Gemini), devolviendo un análisis de sentimiento y predicción de tendencias.

---

## 🏗️ Arquitectura y Diseño del Sistema

El proyecto está diseñado bajo los principios de **Clean Architecture**, asegurando la separación de responsabilidades y la escalabilidad de las fuentes de datos (MVP V1.0):

* **📊 Ingestión Cuantitativa (El Latido):** Extracción asíncrona de datos de precios y volumen a través de la API pública de Binance.
* **📰 Ingestión Cualitativa (El Termómetro):** Agregación de los últimos titulares del mercado cripto para evaluar el sentimiento social y el pánico/euforia.
* **🧠 Motor de Inferencia AI (Gemini):** Procesamiento del contexto combinado mediante técnicas de *Prompt Engineering* estricto para devolver estructuras JSON válidas con puntuaciones de sentimiento.
* **⚡ Framework Asíncrono:** Desarrollado sobre FastAPI y `httpx` para manejar peticiones de red concurrentes sin bloqueos (I/O Bound operations).

---

## 🛠️ Stack Tecnológico

* **Backend Framework:** Python 3.12+ / FastAPI
* **Inteligencia Artificial:** Google AI Studio (Gemini API)
* **Peticiones HTTP:** Httpx (Asynchronous HTTP Client)
* **Fuentes de Datos:** Binance API / CryptoPanic API

---

## 🚀 Instalación y Uso Local (Modo Desarrollo)

*(Las instrucciones se irán completando a medida que desarrollemos el proyecto)*

1. Clona el repositorio:
   ```bash
   git clone [https://github.com/davidValades/cryptosentiment-ai.git](https://github.com/davidValades/cryptosentiment-ai.git)
   cd cryptosentiment-ai
   ```
