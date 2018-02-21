import logger
from pathlib import Path
import yaml


def decorate(inventory):
    log = logger.create_logger()
    config = Path('./whitelist.yml')

    if config.is_file():
        log.debug("Opening whitelist file %s", config)
        with open(config, 'r') as stream:
            data_loaded = yaml.load(stream)

    for profile, attribute in inventory.items():
        for region in attribute['Regions']:
            for whitelist_region in data_loaded[profile]:
                if whitelist_region in attribute['Regions']:
                    region.update((v, "True") for k, v in region.items() if k == 'Whitelist')
