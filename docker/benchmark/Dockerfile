FROM python:3.8-buster

WORKDIR /app
RUN python -m pip install --no-cache-dir --upgrade pip

COPY pyproject.toml setup.cfg ./
COPY src/ src/

RUN pip install --no-cache-dir --upgrade -e .[benchmark]
