FROM python:3.9

WORKDIR /api-gateway

COPY ./README.md /api-gateway/README.md

COPY ./requirements.txt /api-gateway/requirements.txt

COPY .env /api-gateway/.env

COPY ./setup.py /api-gateway/setup.py

COPY ./source /api-gateway/source

RUN pip install --upgrade pip

RUN pip install -e /api-gateway/.

CMD ["python", "/api-gateway/source/main.py"]
