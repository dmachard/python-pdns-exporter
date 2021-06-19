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

class TestCase(unittest.TestCase):
    def assertIsFile(self, path):
        pl = pathlib.Path(path)
        if not pathlib.Path(pl).resolve().is_file():
            raise AssertionError("File does not exist: %s" % str(path))

class TestExport(TestCase):
    def test_export_mysql_invalid_host(self):
        """invalid host database"""
        with self.assertRaises(pymysql.err.OperationalError) as cm:
            exporter = pdns_exporter.PdnsExporter(host="128.0.0.2", port=port, user=user, 
                                                  passwd=passwd, db=db, connect_timeout=1)
            exporter.export()
        
    def test_export_mysql_invalid_credentials(self):
        """invalid database credentials"""
        with self.assertRaises(pymysql.err.OperationalError) as cm:
            exporter = pdns_exporter.PdnsExporter(host=host, port=port, user=user, passwd="", db=db)
            exporter.export()
        
    def test_export_mysql_to_bind_zone(self):
        """export to bind zone format"""  
        path_zone =  "/tmp/db.test.internal"     
        if os.path.exists(path_zone): os.remove(path_zone)     

        # run the exporter
        exporter = pdns_exporter.PdnsExporter(host=host, port=port, user=user, passwd=passwd, db=db)
        exporter.export()

        self.assertIsFile(path_zone)