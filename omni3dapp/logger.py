import logging

logging.basicConfig(filename='omni3dapp.log',
                    format='%(asctime)s %(levelname)s:%(message)s',
                    level=logging.DEBUG)
log = logging.getLogger(__name__)
