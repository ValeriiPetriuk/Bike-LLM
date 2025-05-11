# chatbot_api/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Оновлюємо pip і очищаємо кеш
RUN pip install --upgrade pip && \
    pip cache purge

COPY ./src/ /app

COPY ./pyproject.toml /code/pyproject.toml
RUN pip install /code/.  --default-timeout=100 future

EXPOSE 8000
CMD ["sh", "entrypoint.sh"]