# pdns-records-exporter

This is a python module to export PowerDNS records database in several ways:
- export dns records to bind zone format
- export dns records metrics

Two modes are available to use this module:
- by importing directly the module in your code
- by running the server

## Installation

This module can be installed from [pypi](https://pypi.org/project/pdns_records_exporter/) website

```python
pip install pdns_records_exporter
```

## Export DNS records

To export PowerDNS recors, you need to configure the Exporter with your credentials database.

```python
import pdns_records_exporter

host = "localhost"
port = 3306
user = "user"
passwd = "*****"
db = "powerdns"

handler = pdns_records_exporter.Exporter(host=host, port=port, user=user, passwd=passwd, db=db)
handler.export()
```

By default, the dns zone files are created in the /tmp folder.