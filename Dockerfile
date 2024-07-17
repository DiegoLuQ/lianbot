# Usa una imagen de Python como base
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de la aplicación y los requisitos al contenedor
COPY ./app/requirements.txt ./app/requirements.txt

COPY ./app /app/
# EXPOSE 90
# Instala las dependencias de Python
RUN pip install --no-cache-dir --upgrade -r ./app/requirements.txt

# Expone el puerto 5000 para que Flask pueda recibir solicitudes
