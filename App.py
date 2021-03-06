import logging
import socket
import os.path
from codeitsuisse import app

logger = logging.getLogger(__name__)


@app.route('/', methods=['GET'])
def default_route():
    return "Python Template"


logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    logging.info("Starting application ...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    if os.path.isfile('./local'):
        port = 3000
    else:
        port = sock.getsockname()[1]
    sock.close()
    app.run(port=port)
