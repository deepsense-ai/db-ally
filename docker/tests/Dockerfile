FROM python:3.8-buster

WORKDIR /tests
RUN python -m pip install --no-cache-dir --upgrade pip

COPY pyproject.toml setup.cfg requirements-dev.txt check_licenses.sh ./
COPY src/ src/
COPY data/ data/
COPY benchmark/ benchmark/

RUN pip install build twine bump2version wheel==0.41.3
RUN pip install --no-cache-dir --upgrade -e .[benchmark]
RUN pip install -r requirements-dev.txt
RUN pip install openai~=1.10.0
