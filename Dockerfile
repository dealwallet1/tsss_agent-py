FROM python:3.12

RUN pip3 install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock /app/.

COPY . /app/.

RUN poetry install

EXPOSE 4053

ENTRYPOINT ["poetry", "run", "python", "agent_server.py"]
