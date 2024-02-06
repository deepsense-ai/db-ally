FROM python:3.8-buster

WORKDIR /benchmark
RUN python -m pip install --no-cache-dir --upgrade pip

COPY pyproject.toml setup.cfg ./
COPY src/ src/
COPY data/ data/

RUN pip install --no-cache-dir --upgrade -e .[benchmark]
RUN pip install openai~=1.10.0
