# 1. Usar una imagen base de Python
FROM python:3.9-slim

# 2. Instalar libgomp1 (necesario para LightGBM)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 3. Establecer un directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiar las dependencias (requirements.txt) al contenedor
COPY env/requirements.txt /app/

# 5. Instalar las librerías
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar el resto del proyecto al contenedor
COPY . /app/

# 7. Crear un alias para 'python' que apunte a 'python3'
RUN ln -sf /usr/bin/python3 /usr/bin/python

# 8. Asegurar permisos de ejecución para app.py
RUN chmod +x src/app.py

# 9. Establecer permisos de lectura para index.html y modelo entrenado
RUN chmod 755 web/index.html
RUN chmod 644 models/trained_model.pkl

# 10. Crear la carpeta '../data' dentro del contenedor
RUN mkdir -p /app/data

# 11. Asegurar permisos de escritura en la carpeta de predicciones
RUN chmod 777 /app/data

# 12. Exponer el puerto 5000 para Flask
EXPOSE 5000

# 13. Configurar el punto de entrada para servir la aplicación Flask
CMD ["python", "src/app.py"]
