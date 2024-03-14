FROM python:3.11-slim-bullseye
ENV TZ="America/Sao_Paulo"

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

#Prepare the environment
RUN apt update && \
pip install --no-cache-dir --upgrade pip && \
pip install poetry

WORKDIR /usr/src/app

COPY pyproject.toml ./

RUN poetry config virtualenvs.create false && \
poetry install --no-dev --no-interaction --no-ansi

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8001

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

CMD ["--host", "0.0.0.0", "--port", "8001", "--reload"]