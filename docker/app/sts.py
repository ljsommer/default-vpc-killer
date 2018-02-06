import boto3
from botocore.exceptions import ClientError
import logger


def account_id(inventory):
    log = logger.create_logger()
    region = 'us-west-2'

    for profile, attribute in inventory.items():

        try:
            session = boto3.Session(
                profile_name=profile,
                region_name=region
            )

            account_id = session.client('sts').get_caller_identity()['Account']
            inventory[profile]['AccountId'] = account_id

        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidClientTokenId':
                log.warn("""The keypair associated with profile %s
                    is not currently able to authenticate against AWS STS.
                    Please investigate or remove and rerun.""", profile)
            else:
                log.warn("Unhandled exception occurred: %s", e)
                continue
