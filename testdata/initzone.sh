#!/bin/bash

sudo docker exec powerdns pdnsutil create-zone zone.test ns1.zone.test
sudo docker exec powerdns pdnsutil add-record zone.test ns1 A 3600 128.0.0.1
sudo docker exec powerdns pdnsutil add-record zone.test a A 300 128.0.0.2 
sudo docker exec powerdns pdnsutil add-record zone.test a2 A 300 128.0.0.2 128.0.0.3
sudo docker exec powerdns pdnsutil add-record zone.test aaaa AAAA 300 fe80::42:1eff:feed:f6d6
sudo docker exec powerdns pdnsutil add-record zone.test cname CNAME 300 a.zone.test
sudo docker exec powerdns pdnsutil add-record zone.test txt TXT 300 '"hello world"'