
import logging
import sys

def setup_logger(name):
    logger = logging.getLogger(name)

    loglevel = logging.DEBUG
    logfmt = '%(asctime)s %(levelname)s %(message)s'
    logger.setLevel(loglevel)
    lh = logging.StreamHandler(stream=sys.stdout)
    lh.setLevel(loglevel)
    lh.setFormatter(logging.Formatter(logfmt))    
    logger.addHandler(lh)
    return logger

def start_exporter():
    """start exporter as server"""
    pass