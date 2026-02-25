FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# CETTE LIGNE EST LA CLÉ : elle installe le navigateur EXACT que ta version Python veut
RUN playwright install chromium

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]