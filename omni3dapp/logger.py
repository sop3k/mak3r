import logging

LEVEL = logging.DEBUG

logging.basicConfig(
    filename='omni3dapp.log',
    format='%(asctime)s - %(module)s:%(funcName)s - %(levelname)s:%(message)s',
    level=LEVEL)
log = logging.getLogger(__name__)
