import boto3
from botocore.exceptions import ClientError
import logger


def account_id(inventory, profiles):
    log = logger.create_logger()
    region = 'us-west-2'

    for profile in profiles:

        try:
            session = boto3.Session(
                profile_name=profile,
                region_name=region
            )

            account_id = session.client('sts').get_caller_identity()['Account']

            inventory[account_id] = {}
            inventory[account_id]['ProfileName'] = profile

        except ClientError as error:
            if error.response['Error']['Code'] == 'InvalidClientTokenId':
                log.warn("""The keypair associated with profile %s
                    is not currently able to authenticate against AWS STS.
                    Please investigate or remove and rerun.""", profile)
            else:
                log.warn("Unhandled exception occurred: %s", error)
                continue
