FROM python:3.12-slim

# 1. Crear el usuario primero
# Usamos -m para crear el home y asegurar que el usuario sea válido
RUN useradd -m appuser

# 2. Establecer el directorio de trabajo
WORKDIR /app

# 3. Pre-crear la carpeta de datos
# Le asignamos el dueño de inmediato para que SQLite no tenga problemas
RUN mkdir -p /app/data && chown appuser:appuser /app/data

# 4. Instalar dependencias
# Copiamos solo requirements para aprovechar la caché de capas de Docker
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto de la aplicación
# Usamos --chown aquí para evitar un paso extra de 'RUN chown' que pesaría más
COPY --chown=appuser:appuser . .

# 6. Cambiar al usuario no privilegiado
USER appuser

# Puerto de la API
EXPOSE 8000

# Comando de ejecución
CMD ["uvicorn", "actividad_servidores:app", "--host", "0.0.0.0", "--port", "8000"]