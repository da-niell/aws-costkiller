# Imagen base oficial de Python
FROM python:3.9-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y código
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Comando por defecto: ejecutar el handler como script (opcional)
CMD ["python", "handler.py"]
