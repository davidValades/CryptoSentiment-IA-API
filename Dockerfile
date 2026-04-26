# 1. Usamos una imagen de Python ligera y oficial
FROM python:3.12-slim

# 2. Variables de entorno para que Python no genere basura y los logs se vean en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Carpeta de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalamos librerías del sistema necesarias para SQLite si fuera necesario
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && rm -rf /var/lib/apt/lists/*

# 5. Copiamos el archivo de requerimientos e instalamos todo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiamos todo el código de tu proyecto al contenedor
COPY . .

# 7. Exponemos el puerto 8000 (el de FastAPI)
EXPOSE 8000

# 8. El comando mágico para arrancar la máquina
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]