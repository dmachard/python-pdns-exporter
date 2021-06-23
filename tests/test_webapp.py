
import aiohttp
import aiohttp.test_utils

from pdns_exporter import exporter
from pdns_exporter import webapp

class args:
    c = None
    v = False

BASIC_AUTH = aiohttp.BasicAuth("changeme", "changeme")

class TestWebapp(aiohttp.test_utils.AioHTTPTestCase):
    async def get_application(self):
        """get webapp"""
        cfg = exporter.setup_config(args=args())
        return webapp.setup_webapp(cfg=cfg)

    @aiohttp.test_utils.unittest_run_loop
    async def test_invalid_auth_zones(self):
        """invalid basic authentication for /zones"""
        async with self.client.get("/zones") as r:
            print(r.status)
            assert r.status == 401

    @aiohttp.test_utils.unittest_run_loop
    async def test_invalid_auth_zone(self):
        """invalid basic authentication for /zone/id"""
        async with self.client.get("/zone/1") as r:
            print(r.status)
            assert r.status == 401

    @aiohttp.test_utils.unittest_run_loop
    async def test_invalid_auth_metrics(self):
        """invalid basic authentication for /metrics"""
        async with self.client.get("/metrics") as r:
            print(r.status)
            assert r.status == 401

    @aiohttp.test_utils.unittest_run_loop
    async def test_invalid_route(self):
        """invalid route"""
        async with self.client.get("/", auth=BASIC_AUTH) as r:
            print(r.status)
            assert r.status == 404

    @aiohttp.test_utils.unittest_run_loop
    async def test_get_all_zones(self):
        """get all zones"""
        async with self.client.get("/zones", auth=BASIC_AUTH) as r:
            print(r.status)
            assert r.status == 200
            zones = await r.json()
            assert len(zones) > 0

    @aiohttp.test_utils.unittest_run_loop
    async def test_get_one_zone(self):
        """get zone in bind format"""
        async with self.client.get("/zone/1", auth=BASIC_AUTH) as r:
            print(r.status)
            assert r.status == 200
            plaintext = await r.text()
            assert "$ORIGIN ." in plaintext

    @aiohttp.test_utils.unittest_run_loop
    async def test_get_metrics(self):
        """get metrics"""
        async with self.client.get("/metrics", auth=BASIC_AUTH) as r:
            print(r.status)
            assert r.status == 200
            plaintext = await r.text()
            assert "# HELP pdnsexporter_zones" in plaintext
            assert "# HELP pdnsexporter_records" in plaintext