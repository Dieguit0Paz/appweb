# Usamos una imagen de Python ligera y estable
FROM python:3.9-slim

# Evita que Python genere archivos .pyc y asegura que los logs se vean en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para algunas librerías gráficas
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos primero (para aprovechar la caché de Docker)
# Si no tienes un archivo requirements.txt, el comando siguiente lo creará por ti
RUN echo "streamlit\npandas\nplotly\nrequests" > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto de los archivos (app.py, logos, manual de marca, etc.)
COPY . .

# Exponemos el puerto que usa Streamlit por defecto
EXPOSE 8501

# Configuración de Streamlit para que funcione correctamente en entornos de red (como VPS)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Comando para ejecutar la aplicación
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]