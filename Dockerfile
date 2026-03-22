# Usamos una imagen de Python ligera y estable
FROM python:3.9-slim

# Formato correcto de ENV key=value para evitar warnings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo
WORKDIR /app

# Instalamos solo lo estrictamente necesario
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear requirements.txt dinámicamente
RUN echo "streamlit\npandas\nplotly\nrequests" > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos app.py y el logo (asegúrate de que estén en la misma carpeta)
COPY . .

# Puerto por defecto de Streamlit
EXPOSE 8501

# Comprobación de salud del contenedor
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Comando de inicio
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]