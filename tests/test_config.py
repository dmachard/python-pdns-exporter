import unittest
import os

from pdns_exporter import exporter

EXTERNAL_SETTINGS_PATH = "/tmp/pdns-exporter/settings.conf.test"

class args:
    c = None
    v = False

class TestConfig(unittest.TestCase):
    def tearDown(self):
        """clear test data"""
        try:
            os.remove(EXTERNAL_SETTINGS_PATH)
        except: pass

        try:
            os.environ.pop("PDNSEXPORT_LOCAL_PORT")
        except: pass
        
    def test_default_config(self):
        """read default config"""
        # read config
        cfg = exporter.setup_config(args=args())

        self.assertFalse(int(cfg["logs-verbose"]))
        self.assertEqual(cfg["local-address"], "0.0.0.0")
        self.assertEqual(int(cfg["local-port"]), 9090)

    def test_overwrite_config_external(self):
        """overwrite config with external file"""
        _args = args()
        _args.c = EXTERNAL_SETTINGS_PATH

        cfg_ext = ["local-address=127.0.0.1", "local-port=8080"]
        with open(_args.c , "w") as f:
           f.write("\n".join(cfg_ext))

        # read config
        cfg = exporter.setup_config(args=_args)

        assert cfg["local-port"] == "8080"
    
    def test_overwrite_config_env(self):
        """overwrite config with env variables"""
        os.environ['PDNSEXPORT_LOCAL_PORT'] = "8888"

        # read config
        cfg = exporter.setup_config(args=args())

        # remove variable from environment for other test
        os.environ.pop("PDNSEXPORT_LOCAL_PORT")

        self.assertEqual(cfg["local-port"], "8888")
