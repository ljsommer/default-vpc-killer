import logger
from os import path
from pathlib import Path
import yaml


def decorate(inventory, regions):
    log = logger.create_logger()

    pwd, filename = path.split(path.abspath(__file__))
    config = path.join(pwd, 'whitelist.yml')

    if path.isfile(config):
        log.debug("Whitelist configuration file found: %s", config)
        with open(config, 'r') as stream:
            data_loaded = yaml.load(stream)
            log.debug(
                "Whitelist config file contents: %s - no further processing will occur on these items.",
                data_loaded
            )

        for account, attribute in inventory.items():
            for region in attribute['Regions']:
                try:
                    for whitelist_region in data_loaded[attribute['ProfileName']]:
                        for k, v in region.items():
                            if k == whitelist_region:
                                v['Whitelist'] = "True"

                except KeyError as e:
                    log.warn(
                        "Profile identified in whitelist file that is not present in credentials file: %s",
                        e.response['Error']['Body'] 
                    )

        for whitelist_region in data_loaded[attribute['ProfileName']]:
            if whitelist_region not in regions:

                log.warn(
                    "Region identified in whitelist file that was not listed by AWS API call: %s",
                    whitelist_region
                )
    else:
        log.debug("No whitelist configuration file found at path %s", path.abspath(config))







