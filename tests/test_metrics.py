import unittest
import pathlib 
import os
import pymysql

import pdns_exporter

host = "127.0.0.1"
port = 3306
user = "powerdns"
passwd = "powerdns"
db = "powerdns"

class TestMetrics(unittest.TestCase):
    def test_metrics(self):
        """export metrics"""
        exporter = pdns_exporter.PdnsExporter(host=host, port=port, user=user, passwd=passwd, db=db)
        metrics = exporter.metrics()

        self.assertGreater(len(metrics), 0)