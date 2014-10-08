import logging


def configure_logging(name, enabled):
    logger = logging.getLogger(name)

    if not enabled:
        return logger

    logger.setLevel(logging.INFO)

    fh = logging.FileHandler('openvpn_ad_' + name + '.log')
    fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger