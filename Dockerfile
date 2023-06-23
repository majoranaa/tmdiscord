FROM python:3.11-slim

# Install curl.
RUN apt-get -y update
RUN apt-get -y install curl

# Install tini
RUN apt-get -y install tini

# Install poetry.
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.5.1 python3 -
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root --no-interaction --no-ansi --without dev

COPY bin bin/
COPY config config/
COPY tmdiscord tmdiscord/

ENTRYPOINT ["tini", "--", "./bin/run"]
