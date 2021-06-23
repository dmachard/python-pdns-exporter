
import unittest
import subprocess
import requests
import time

from pdns_exporter import exporter

class FakeResp:
    status_code = 0

class TestPackage(unittest.TestCase):
    def test_import(self):
        """test import package"""
        api_url = "http://127.0.0.1:9090/zones"
        r = FakeResp()

        cmd = ["python3", "-c", "from pdns_exporter import exporter; exporter.start_exporter();"]

        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as proc:
            for retry in range(5):
                try:
                    r = requests.get(url=api_url, auth=('changeme', 'changeme'))
                    break
                except requests.exceptions.ConnectionError:
                    time.sleep(0.5)
            proc.kill()

        print(r.status_code)
        assert r.status_code == 200

        