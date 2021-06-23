
import logging
import sys
import argparse
import pkgutil
import pathlib
import configparser
import os

from pdns_exporter import webapp

logger = logging.getLogger("pdnsexporter")

def setup_cli():
    """setup command-line arguments"""
    options = argparse.ArgumentParser()          
    options.add_argument("-c", help="external config file")   
    options.add_argument('-v', action='store_true', help="verbose mode")

    return options

def setup_logger(cfg):
    loglevel = logging.DEBUG if int(cfg["logs-verbose"]) else logging.INFO
    logfmt = '%(asctime)s %(levelname)s %(message)s'
    
    logger.setLevel(loglevel)
    logger.propagate = False
    
    lh = logging.StreamHandler(stream=sys.stdout )
    lh.setLevel(loglevel)
    lh.setFormatter(logging.Formatter(logfmt))    
    
    logger.addHandler(lh)

def setup_config(args):
    """load default config and update it with arguments or external config"""
    cfg = {}
    parser = configparser.ConfigParser()

    # Set the default configuration file
    content = pkgutil.get_data(__package__, 'settings.conf')
    parser.read_string("[DEFAULT]\n" + content.decode())
    cfg = parser.defaults()

    # Overwrites then with the external file ?    
    if args.c: 
        with open(pathlib.Path(args.c), "r") as fd:
            parser.read_string("[DEFAULT]\n" + fd.read())
            cfg_ext = parser.defaults()
        cfg.update(cfg_ext)

    # Or searches for a file named dnstap.conf in /etc/pdns-exporter/       
    else:
        f = pathlib.Path("/etc/pdns-exporter/settings.conf")
        if f.exists():
            with open(pathlib.Path(args.c), "r") as fd:
                parser.read_string("[DEFAULT]\n" + fd.read())
                cfg_ext = parser.defaults()
            cfg.update(cfg_ext)

    # update verbose mode with command line arguments
    if args.v:
        cfg["logs-verbose"] = args.v

    # finally overwrites config with environment variables
    ENV_VERBOSE = os.getenv('PDNSEXPORT_VERBOSE')
    if ENV_VERBOSE is not None:
        cfg["logs-verbose"] = ENV_VERBOSE

    ENV_LOCAL_ADDRESS = os.getenv('PDNSEXPORT_LOCAL_ADDRESS')
    if ENV_LOCAL_ADDRESS is not None:
        cfg["local-address"] = ENV_LOCAL_ADDRESS

    ENV_LOCAL_PORT = os.getenv('PDNSEXPORT_LOCAL_PORT')
    if ENV_LOCAL_PORT is not None:
        cfg["local-port"] = ENV_LOCAL_PORT

    ENV_API_LOGIN = os.getenv('PDNSEXPORT_API_LOGIN')
    if ENV_API_LOGIN is not None:
        cfg["api-login"] = ENV_API_LOGIN

    ENV_API_PWD = os.getenv('PDNSEXPORT_API_PASSWORD')
    if ENV_API_PWD is not None:
        cfg["api-password"] = ENV_API_PWD

    ENV_DB_HOST = os.getenv('PDNSEXPORT_DB_HOST')
    if ENV_DB_HOST is not None:
        cfg["db-pdns-host"] = ENV_DB_HOST

    ENV_DB_PORT = os.getenv('PDNSEXPORT_DB_PORT')
    if ENV_DB_PORT is not None:
        cfg["db-pdns-port"] = ENV_DB_PORT

    ENV_DB_USER = os.getenv('PDNSEXPORT_DB_USER')
    if ENV_DB_USER is not None:
        cfg["db-pdns-user"] = ENV_DB_USER

    ENV_DB_PWD = os.getenv('PDNSEXPORT_DB_PWD')
    if ENV_DB_PWD is not None:
        cfg["db-pdns-password"] = ENV_DB_PWD

    ENV_DB_NAME = os.getenv('PDNSEXPORT_DB_NAME')
    if ENV_DB_NAME is not None:
        cfg["db-pdns-name"] = ENV_DB_NAME

    return cfg

def start_exporter():
    """start exporter as server"""
    # setup command-line arguments.
    options = setup_cli()
    args = options.parse_args()

    # setup config
    cfg = setup_config(args=args)
    
    # setup logger
    setup_logger(cfg=cfg)

    logger.debug("config OK, starting...")

    # setup webserver
    webapp.run(cfg=cfg)