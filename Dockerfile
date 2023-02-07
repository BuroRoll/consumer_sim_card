FROM python:3.10-slim

WORKDIR /code

COPY pyproject.toml  /code/

# Установка локальной таймзоны и русского языка
ENV TZ Asia/Yekaterinburg
ENV LANGUAGE ru_RU.UTF-8
ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y locales  \
    && sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=ru_RU.UTF-8

ENV PATH=${PATH}:/root/.poetry/bin
RUN apt-get update && apt-get install -y curl
RUN python -m pip install --upgrade pip
RUN curl -sSL https://install.python-poetry.org | python3 -  \
    && ~/.local/share/pypoetry/venv/bin/poetry config virtualenvs.create false  \
    && ~/.local/share/pypoetry/venv/bin/poetry install
RUN apt-get remove -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY ./src /code

CMD faust -A request_sim_validity_consumer.app worker