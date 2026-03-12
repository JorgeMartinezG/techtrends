# Imagen base ligera con Python
FROM python:3.8-slim

# Variables para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos requirements e instalamos dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto de la aplicación
COPY . /app/
RUN python init_db.py
# Exponemos el puerto de la app
EXPOSE 3111

# Comando para arrancar la aplicación

CMD ["python", "app.py"]