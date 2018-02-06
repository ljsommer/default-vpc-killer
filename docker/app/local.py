import logger
import os
import re
import sys


def profiles(inventory):
    log = logger.create_logger()

    credentials_file = os.environ['HOME'] + '/.aws/credentials'

    if os.path.exists(credentials_file):
        if not os.path.getsize(credentials_file) > 0:
            log.error("Credentials file empty. Exiting.")
            sys.exit(1)
    else:
        log.error("Credentials file %s missing. Exiting.", credentials_file)
        sys.exit(1)

    log.debug("Credentials file identified as %s", credentials_file)

    with open(credentials_file) as f:
        for line in f:
            if line.startswith("["):
                profile = re.search(r"\[([A-Za-z0-9_]+)\]", line).group()
                profile = profile[1:-1]

                inventory[profile] = {}
                inventory[profile]['ProfileName'] = profile

    profile_names = []
    for k, v in inventory.items():
        profile_names.append(k)

    log.info("Profiles: %s", profile_names)
