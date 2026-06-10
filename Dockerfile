# ── Estágio 1: builder ────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Instala dependências de sistema necessárias para compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python em modo "wheel" para cache eficiente
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# ── Estágio 2: runtime ────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copia wheels do estágio builder e instala sem baixar nada da internet
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels

# Copia código da aplicação mantendo as estruturas de pastas corretas para os módulos do Python
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Diretório de dados (banco SQLite será montado como volume aqui)
# Garante que a pasta /app/data seja criada e pertença ao appuser ANTES de trocar de usuário
RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ="America/Sao_Paulo" \
    DATABASE_URL="sqlite+aiosqlite:////app/data/baby_routine.db"

EXPOSE 8000

# Healthcheck usando o endpoint correto de summary que o seu main.py expõe
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/summary')"

# Comando corrigido para iniciar o uvicorn apontando para a pasta backend onde está o seu main.py
CMD ["python", "-m", "uvicorn", "backend.main:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--workers", "2", \
    "--proxy-headers", \
    "--forwarded-allow-ips", "*"]

