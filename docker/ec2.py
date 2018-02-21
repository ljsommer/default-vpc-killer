import boto3
from botocore.exceptions import ClientError
import logger


def describe_default_vpcs(inventory, regions):
    log = logger.create_logger()

    for profile in inventory:
        for region in regions:
            try:
                session = boto3.Session(profile_name=profile, region_name=region)
                ec2 = session.client('ec2')

                response = ec2.describe_vpcs(
                    Filters=[
                        {
                            'Name': 'isDefault',
                            'Values': [
                                'true',
                            ]
                        }
                    ]
                )

            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidClientTokenId':
                    log.warn("""The keypair associated with profile %s
                        is not currently able to authenticate against AWS EC2.
                        Please investigate or remove and rerun.""", profile)
                else:
                    log.warn("Unhandled exception occurred: %s", e)
                    continue

            for vpc in response['Vpcs']:
                inventory[profile]['Regions'] = []

                region_dict = {'DefaultVpc': vpc['VpcId'], 'ContainsInstances': False, 'Whitelist': False}

                inventory[profile]['Regions'].append({region: region_dict})


def describe_regions(inventory):
    log = logger.create_logger()
    profile = next(iter(inventory))

    log.debug("Using profile %s to identify available regions ...", profile)

    session = boto3.Session(profile_name=profile)
    ec2 = session.client('ec2')

    try:
        response = ec2.describe_regions()

    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidClientTokenId':
            log.warn("""The keypair associated with profile %s
                is not currently able to authenticate against AWS EC2.
                Please investigate or remove and rerun.""", profile)
        else:
            log.warn("Unhandled exception occurred: %s", e)

    regions = []
    for region in response['Regions']:
        for k, v in region.items():
            if k == "RegionName":
                regions.append(v)

    log.debug("Regions identified: %s", regions)

    return regions


def instances(inventory):
    log = logger.create_logger()

    for profile, attribute in inventory.items():
        for region in attribute['Regions']:
            for key, value in region.items():
                region_name = key
                vpc = value['DefaultVpc']

                try:
                    session = boto3.Session(
                        profile_name=profile,
                        region_name=region_name
                    )

                    ec2_client = session.client('ec2')

                    response = ec2_client.describe_instances(
                        Filters=[
                            {
                                'Name': 'vpc-id',
                                'Values': [
                                    vpc,
                                ]
                            }
                        ]
                    )

                    for k, v in response.items():
                        if k == 'Reservations':
                            if not v:
                                log.debug(
                                    "Account ID %s associated with keypair name %s: Default VPC %s in region %s has no EC2 instances.",
                                    attribute['AccountId'], profile, vpc, region_name
                                )
                                continue

                            else:
                                log.warn(
                                    "Account ID %s associated with keypair name %s: Default VPC %s in region %s has EC2 instances. Skipping.",
                                    attribute['AccountId'], profile, vpc, region_name
                                )

                                for region in inventory[profile]['Regions']:
                                    region.update((v, "False") for k, v in region.items() if k == 'InstancesPresent')
                                continue

                except ClientError as e:
                    if e.response['Error']['Code'] == 'InvalidClientTokenId':
                        log.warn(
                            "The keypair associated with profile %s is not currently able to authenticate against AWS EC2. Please investigate or remove and rerun.", profile)

                    else:
                        log.warn("Unhandled exception occurred: %s", e)
                        continue

def subnets(inventory):
    log = logger.create_logger()

    for profile, attribute in inventory.items():
        for region in attribute['Regions']:
            for key, value in region.items():
                region_name = key
                vpc = value['DefaultVpc']

                try:
                    session = boto3.Session(
                        profile_name=profile,
                        region_name=region_name
                    )

                    ec2_client = session.client('ec2')

                    response = ec2_client.describe_subnets(
                        Filters=[
                            {
                                'Name': 'vpc-id',
                                'Values': [
                                    vpc,
                                ]
                            }
                        ]
                    )

                    for k, v in response.items():
                        if not v:
                            log.debug(
                                "Account ID %s associated with keypair name %s: Default VPC %s in region %s has no EC2 instances.",
                                attribute['AccountId'], profile, vpc, region_name
                            )
                            continue

                        else:
                            log.warn(
                                "Account ID %s associated with keypair name %s: Default VPC %s in region %s has EC2 instances. Skipping.",
                                attribute['AccountId'], profile, vpc, region_name
                            )

                            for region in inventory[profile]['Regions']:
                                region.update((v, "False") for k, v in region.items() if k == 'InstancesPresent')
                            continue

                except ClientError as e:
                    if e.response['Error']['Code'] == 'InvalidClientTokenId':
                        log.warn(
                            "The keypair associated with profile %s is not currently able to authenticate against AWS EC2. Please investigate or remove and rerun.", profile)

                    else:
                        log.warn("Unhandled exception occurred: %s", e)
                        continue





def security_groups(inventory):
    pass

def network_acls(inventory):
    pass

def vpns(inventory):
    pass

def internet_gws(inventory):
    pass

def route_tables(inventory):
    pass

def network_interfaces(inventory):
    pass

def vpc_peering(inventory):
    pass

