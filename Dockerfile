FROM python:3.9

ECHO "CipherString = DEFAULT@SECLEVEL=1" >> /etc/ssl/openssl.cnf

WORKDIR /api-gateway

COPY ./README.md /api-gateway/README.md

COPY ./requirements.txt /api-gateway/requirements.txt

COPY ./setup.py /api-gateway/setup.py

COPY ./source /api-gateway/source

COPY ./.env /api-gateway/source/.env

RUN pip install -e /api-gateway/.

RUN mkdir /gallery-files

CMD ["python", "/api-gateway/source/main.py"]
