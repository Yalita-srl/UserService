# 1. Usar una imagen base de Python
FROM python:3.11-slim

# 2. Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Establecer el directorio de trabajo
WORKDIR /app

# 4. Instalar dependencias
# Copiar solo el archivo de requerimientos para aprovechar el cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el código del proyecto al contenedor
COPY . .

# 6. Recolectar archivos estáticos
RUN python manage.py collectstatic --noinput

# 7. Exponer el puerto en el que correrá Gunicorn
EXPOSE 8000

# 7. Comando para ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "user_service.wsgi:application", "--bind", "0.0.0.0:8000"]
