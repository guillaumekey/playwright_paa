# On prend une image qui a déjà Chrome installé proprement
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# On installe tes bibliothèques Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# On copie ton main.py
COPY . .

# On lance l'API sur le port 10000 (celui de Render)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]