import logging

logging.basicConfig(
    level=logging.WARNING,
    filename="../../difs/logs.log",
    filemode="a",
    format="%(asctime)s %(levelname)s %(funcName)s %(message)s")

logs = logging.getLogger()