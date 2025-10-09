FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Instala Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copia pyproject.toml e lock para cache
COPY pyproject.toml poetry.lock* ./

# Instala dependências do projeto
RUN poetry install --no-root --no-interaction --no-ansi

# Garante que Django fique globalmente disponível
RUN poetry run pip install django

# Copia todo o código
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
