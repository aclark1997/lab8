FROM python:latest
RUN pip install poetry
COPY . /app
WORKDIR /app
RUN poetry install --no-root
RUN poetry add aiohttp
ENTRYPOINT bash
