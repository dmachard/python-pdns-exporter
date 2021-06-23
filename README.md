# Python PowerDNS Records Exporter

This module can be used to export PowerDNS records database in several ways:
- to bind zone format
- records metrics for Prometheus


## Installation

### PyPI

Deploy the pdns records exporter in your server with the pip command.

```python
pip install pdns_exporter
```

After installation, you can execute the `pdns_exporter` to start-it.
By default, the server is listening on the tcp port `9090`.

See [config file](/pdns_exporter/settings.conf) example for more options.

### Docker Hub

Pull the pdns exporter image from Docker Hub.

```bash
docker pull dmachard/pdns-exporter:latest
```

Deploy the container

```bash
docker run -d -p 9090:9090 --name=pdnsexporter01 dmachard/pdns-exporter
```

The container can be configured with the following environment variables:

| Variables | Description |
| ------------- | ------------- |
| PDNSEXPORT_VERBOSE | 1 or 0 to enable verbose mode |
| PDNSEXPORT_LOCAL_ADDRESS | listening ip address of the server |
| PDNSEXPORT_LOCAL_PORT | listening port |
| PDNSEXPORT_API_LOGIN | login for basic authentication |
| PDNSEXPORT_API_PASSWORD | password for basic authentication |
| PDNSEXPORT_DB_HOST | Ip address of your database powerdns server |
| PDNSEXPORT_DB_PORT | Port of your database powerdns server  |
| PDNSEXPORT_DB_USER | User database of your powerdns server  |
| PDNSEXPORT_DB_PWD | Password database of your powerdns server  |
| PDNSEXPORT_DB_NAME | Database name of your powerdns server |


## HTTP API

### Security

Basic authentication method is only supported, don't forget to change the default login and password in settings.conf.

### Swagger

See the [swagger](https://generator.swagger.io/?url=https://raw.githubusercontent.com/dmachard/python-pdns-exporter/master/swagger.yml) documentation.

## Examples

Get all dns zones 

```bash
$ curl -u changeme:changeme http://127.0.0.1:9090/zones | jq .
[
  {
    "id": 1,
    "name": "zone.test"
  }
]
```

Get a specific zone with zone file format

```bash
$ curl -u changeme:changeme http://127.0.0.1:9090/zone/1
$ORIGIN .
zone.test	3600	IN	SOA	a.misconfigured.dns.server.invalid hostmaster.zone.test 0 10800 3600 604800 3600
zone.test	3600	IN	NS	ns1.zone.test
ns1.zone.test	3600	IN	A	128.0.0.1
a.zone.test	300	IN	A	128.0.0.2
a2.zone.test	300	IN	A	128.0.0.2
a2.zone.test	300	IN	A	128.0.0.3
aaaa.zone.test	300	IN	AAAA	fe80::42:1eff:feed:f6d6
cname.zone.test	300	IN	CNAME	a.zone.test
txt.zone.test	300	IN	TXT	"hello world"
```

Get metrics for prometheus of each dns zones declared in your dns server

```bash
$ curl -u changeme:changeme http://127.0.0.1:9090/metrics
# HELP pdnsexporter_zones_total Total number of zones
# TYPE pdnsexporter_zones_total counter
pdnsexporter_zones_total 4
# HELP pdnsexporter_records_total Total number of records
# TYPE pdnsexporter_records_total counter
pdnsexporter_records_total 32
...
```

See [metrics file](/metrics.txt) example.

## Development

### Run 

the dnstap receiver from source

```bash
sudo python3 -c "from pdns_exporter import exporter; exporter.start_exporter();" -v
```

### Testunits

```bash
sudo python3 -m unittest -v
```

### Build docker image

```bash
sudo docker build . --file Dockerfile -t pdns-exporter
```

## About

| | |
| ------------- | ------------- |
| Author | Denis Machard <d.machard@gmail.com> |
| PyPI | https://pypi.org/project/python-pdns-exporter/ |
| Github | https://github.com/dmachard/python-pdns-exporter|
| DockerHub | https://hub.docker.com/r/dmachard/pdns-exporter |
| | |
