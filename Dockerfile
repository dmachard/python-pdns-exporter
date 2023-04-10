FROM python:3.11.3-alpine

LABEL name="Python PowerDNS records exporter" \
      description="Python PowerDNS records exporter" \
      url="https://github.com/dmachard/python-pdns-exporter" \
      maintainer="d.machard@gmail.com"
      
WORKDIR /home/pdnsexporter

COPY . /home/pdnsexporter/

RUN true \
    && apk update \
    && apk add gcc g++ musl-dev \
    && adduser -D exporter \
    && pip install --no-cache-dir -r requirements.txt\
    && apk del gcc g++ musl-dev \
    && cd /home/pdnsexporter \
    && sed -i 's/local-address=127.0.0.1/local-address=0.0.0.0/g' ./pdns_exporter/settings.conf \
    && chown -R exporter:exporter /home/pdnsexporter \
    && true
    
USER exporter

EXPOSE 9090/tcp

ENTRYPOINT ["python", "-c", "from pdns_exporter import exporter;exporter.start_exporter();"]