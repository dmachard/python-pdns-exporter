import unittest
import pathlib 
import os
import configparser

import pdns_exporter

class TestExport(unittest.TestCase):
    def tearDown(self):
        """clear test data"""
        try:
            os.remove( "/etc/powerdns/pdns.conf.test")
        except: pass
        
    def test_config_default(self):
        """default config"""  

        with self.assertLogs('exporter', level='DEBUG') as cm:
            exporter = pdns_exporter.PdnsExporter()
            exporter.search_config(search_local=False)

        self.assertEqual(cm.output, ['DEBUG:exporter:loading default configuration'])

    def test_config_powerdns_valid(self):
        """valid config"""
        path_cfg =  "/etc/powerdns/pdns.conf.test"

        cfg = ["launch=gmysql", "gmysql-host=127.0.0.1", "gmysql-port=3306", 
               "gmysql-dbname=powerdns", "gmysql-user=powerdns", "gmysql-password=powerdns"]
        with open(path_cfg, "w") as f:
           f.write("\n".join(cfg))

        with self.assertLogs('exporter', level='DEBUG') as cm:
            exporter = pdns_exporter.PdnsExporter()
            exporter.search_config()

        self.assertEqual(cm.output, ['DEBUG:exporter:reading configuration from /etc/powerdns/pdns.conf.test'])

    def test_config_powerdns_invalid1(self):
        """invalid powerdns config"""
        path_cfg =  "/etc/powerdns/pdns.conf.test"

        with open(path_cfg, "w") as f:
            f.write("invalid")

        with self.assertRaises(configparser.ParsingError) as cm:
            exporter = pdns_exporter.PdnsExporter()
            exporter.search_config()

    def test_config_powerdns_invalid2(self):
        """invalid powerdns config; key missing"""
        path_cfg =  "/etc/powerdns/pdns.conf.test"

        cfg = ["gmysql-host=127.0.0.1", "gmysql-port=3306"]
        with open(path_cfg, "w") as f:
           f.write("\n".join(cfg))

        with self.assertRaises(configparser.NoOptionError) as cm:
            exporter = pdns_exporter.PdnsExporter()
            exporter.search_config()