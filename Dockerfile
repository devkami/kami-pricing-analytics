FROM python:3.11-slim-bullseye

ENV TZ="America/Sao_Paulo"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    curl \
    libmariadb-dev \
    pkg-config && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install poetry

WORKDIR /usr/src/app

COPY pyproject.toml ./

RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

COPY . .

EXPOSE 8001

RUN chmod +x /usr/src/app/bash_scripts/entrypoint.sh

ENTRYPOINT ["/usr/src/app/bash_scripts/entrypoint.sh"]
CMD ["--host", "0.0.0.0", "--port", "8001", "--reload"]
