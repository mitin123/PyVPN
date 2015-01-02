import logging

def create_logger(name="default", file="./app.log", level=logging.WARNING):
    logger = logging.getLogger(name)
    hdlr = logging.FileHandler(file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(level)
    return logger


def address_in_subnet(subnet, address):
    pass