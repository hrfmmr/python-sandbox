import logging.config

import yaml


def setup_logger(yaml_file):
    with open(yaml_file) as f:
        config = yaml.load(f.read(), Loader=yaml.Loader)
    logging.config.dictConfig(config)
