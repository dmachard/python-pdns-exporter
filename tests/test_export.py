import unittest
import pathlib 
import os

import pdns_records_exporter

host = "localhost"
port = 3306
user = "powerdns_user"
passwd = "powerdns_user_password"
db = "powerdns"

class TestCase(unittest.TestCase):
    def assertIsFile(self, path):
        pl = pathlib.Path(path)
        if not pathlib.Path(pl).resolve().is_file():
            raise AssertionError("File does not exist: %s" % str(path))

class TestExport(TestCase):
    def test_export(self):
        """export"""  
        path_zone =  "/tmp/db.test.internal"     
        if os.path.exists(path_zone): os.remove(path_zone)     

        self.exporter = pdns_records_exporter.Exporter(host=host, port=port, user=user, passwd=passwd, db=db)
        self.exporter.export()
        self.assertIsFile(path_zone)