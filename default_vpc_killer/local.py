import os
import re
import sys
import logger


def profiles():
    log = logger.create_logger()

    profiles = []

    aws_dir = os.environ['HOME'] + '/.aws/'
    credentials_file = os.environ['HOME'] + '/.aws/credentials'

    log.debug("Root dir contents: %s", os.listdir(os.environ['HOME']))
    log.debug("Mounted .aws dir contents: %s", os.listdir(aws_dir))

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
                profile = re.search(r"\[([A-Za-z0-9\-\_]+)\]", line).group()
                profile = profile[1:-1]

                profiles.append(profile)

    log.debug("Profiles: %s", profiles)

    return profiles
