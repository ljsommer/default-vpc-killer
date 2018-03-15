import boto3
from botocore.exceptions import ClientError
import logger


def describe_default_vpcs(inventory, regions):
    log = logger.create_logger()

    for account in inventory:
        inventory[account]['Regions'] = []

        for region in regions:
            try:
                session = boto3.Session(profile_name=inventory[account]['ProfileName'], region_name=region)
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
                region_dict = {'DefaultVpc': vpc['VpcId'], 'NetworkInterfacesPresent': False, 'Whitelist': False}
                inventory[account]['Regions'].append({region: region_dict})


def describe_regions(profiles):
    log = logger.create_logger()

    for profile in profiles:
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


def network_interfaces(inventory):
    log = logger.create_logger()

    for account, attribute in inventory.items():
        for region in attribute['Regions']:
            for key, value in region.items():
                region_name = key
                vpc = value['DefaultVpc']

                if not value['Whitelist']:

                    try:
                        session = boto3.Session(
                            profile_name=attribute['ProfileName'],
                            region_name=region_name
                        )

                        ec2_client = session.client('ec2')

                        response = ec2_client.describe_network_interfaces(
                            Filters=[
                                {
                                    'Name': 'vpc-id',
                                    'Values': [
                                        vpc,
                                    ]
                                }
                            ]
                        )

                        if not response['NetworkInterfaces']:
                            log.debug(
                                "Account ID %s associated with keypair name %s: No network interfaces present in %s",
                                account, attribute['ProfileName'], vpc
                            )

                        else:
                            log.warn(
                                "Account ID %s associated with keypair name %s: Network interfaces found in %s. No action will be taken on this VPC.",
                                account, attribute['ProfileName'], vpc
                            )

                            for vpc in inventory[account]['Regions']:
                                vpc.update((v, "True") for k, v in vpc.items() if k == 'NetworkInterfaces')
                            continue

                    except ClientError as e:
                        if e.response['Error']['Code'] == 'InvalidClientTokenId':
                            log.warn(
                                "The keypair associated with profile %s is not currently able to authenticate against AWS EC2. Please investigate or remove and rerun.",
                                profile
                            )

                        else:
                            log.warn("Unhandled exception occurred: %s", e)
                            continue


def subnets(inventory, dry_run):
    log = logger.create_logger()

    for _account, attribute in inventory.items():
        for region in attribute['Regions']:
            for key, value in region.items():
                region_name = key
                vpc = value['DefaultVpc']

                if not value['NetworkInterfacesPresent'] and not value['Whitelist']:

                    try:
                        session = boto3.Session(
                            profile_name=attribute['ProfileName'],
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

                        for subnet in response['Subnets']:
                            subnet_dict = subnet
                            resource = subnet_dict['SubnetId']

                            log.debug("Attempting to delete %s from %s - dry-run: %s", resource, vpc, dry_run)
                            response = ec2_client.delete_subnet(
                                SubnetId=resource,
                                DryRun=dry_run
                            )

                    except ClientError as e:
                        if e.response['Error']['Code'] == 'InvalidClientTokenId':
                            log.warn(
                                "The keypair associated with profile %s is not currently able to authenticate against AWS EC2. Please investigate or remove and rerun.",
                                profile
                            )

                        else:
                            log.warn("Unhandled exception occurred: %s", e)
                            continue


def security_groups(inventory, dry_run):
    log = logger.create_logger()

    for _account, attribute in inventory.items():
        for region in attribute['Regions']:
            for key, value in region.items():
                region_name = key
                vpc = value['DefaultVpc']

                if not value['NetworkInterfacesPresent'] and not value['Whitelist']:

                    try:
                        session = boto3.Session(
                            profile_name=attribute['ProfileName'],
                            region_name=region_name
                        )

                        ec2_client = session.client('ec2')

                        response = ec2_client.describe_security_groups(
                            Filters=[
                                {
                                    'Name': 'vpc-id',
                                    'Values': [
                                        vpc,
                                    ]
                                }
                            ]
                        )

                        for security_group in response['SecurityGroups']:
                            security_group_dict = security_group
                            resource = security_group_dict['GroupId']

                            log.debug("Attempting to delete %s from %s - dry-run: %s", resource, vpc, dry_run)
                            response = ec2_client.delete_security_group(
                                GroupId=resource,
                                DryRun=dry_run
                            )

                    except ClientError as e:
                        if e.response['Error']['Code'] == 'InvalidClientTokenId':
                            log.warn(
                                "The keypair associated with profile %s is not currently able to authenticate against AWS EC2. Please investigate or remove and rerun.",
                                profile
                            )

                        else:
                            log.warn("Unhandled exception occurred: %s", e)
                            continue


def network_acls(inventory, dry_run):
    log = logger.create_logger()

    for _account, attribute in inventory.items():
        for region in attribute['Regions']:
            for key, value in region.items():
                region_name = key
                vpc = value['DefaultVpc']

                if not value['NetworkInterfacesPresent'] and not value['Whitelist']:

                    try:
                        session = boto3.Session(
                            profile_name=attribute['ProfileName'],
                            region_name=region_name
                        )

                        ec2_client = session.client('ec2')

                        response = ec2_client.describe_network_acls(
                            Filters=[
                                {
                                    'Name': 'vpc-id',
                                    'Values': [
                                        vpc,
                                    ]
                                }
                            ]
                        )

                        for nacl in response['NetworkAcls']:
                            resource = nacl['NetworkAclId']

                            log.debug("Attempting to delete %s from %s - dry-run: %s", resource, vpc, dry_run)
                            response = ec2_client.delete_network_acl(
                                NetworkAclId=resource,
                                DryRun=dry_run
                            )

                    except ClientError as e:
                        if e.response['Error']['Code'] == 'InvalidClientTokenId':
                            log.warn(
                                "The keypair associated with profile %s is not currently able to authenticate against AWS EC2. Please investigate or remove and rerun.",
                                profile
                            )

                        else:
                            log.warn("Unhandled exception occurred: %s", e)
                            continue


def internet_gateways(inventory, dry_run):
    log = logger.create_logger()

    for _account, attribute in inventory.items():
        for region in attribute['Regions']:
            for key, value in region.items():
                region_name = key
                vpc = value['DefaultVpc']

                if not value['NetworkInterfacesPresent'] and not value['Whitelist']:

                    try:
                        session = boto3.Session(
                            profile_name=attribute['ProfileName'],
                            region_name=region_name
                        )

                        ec2_client = session.client('ec2')

                        response = ec2_client.describe_internet_gateways(
                            Filters=[
                                {
                                    'Name': 'attachment.vpc-id',
                                    'Values': [
                                        vpc,
                                    ]
                                }
                            ]
                        )

                        for igw in response['InternetGateways']:
                            resource = igw['InternetGatewayId']

                            response = ec2_client.detach_internet_gateway(
                                DryRun=dry_run,
                                InternetGatewayId=resource,
                                VpcId=vpc
                            )

                            log.debug("Attempting to delete %s from %s - dry-run: %s", resource, vpc, dry_run)
                            response = ec2_client.delete_internet_gateway(
                                InternetGatewayId=resource,
                                DryRun=dry_run
                            )

                    except ClientError as e:
                        if e.response['Error']['Code'] == 'InvalidClientTokenId':
                            log.warn(
                                "The keypair associated with profile %s is not currently able to authenticate against AWS EC2. Please investigate or remove and rerun.",
                                profile
                            )

                        else:
                            log.warn("Unhandled exception occurred: %s", e)
                            continue


def route_tables(inventory, dry_run):
    log = logger.create_logger()

    for _account, attribute in inventory.items():
        for region in attribute['Regions']:
            for key, value in region.items():
                region_name = key
                vpc = value['DefaultVpc']

                if not value['NetworkInterfacesPresent'] and not value['Whitelist']:

                    try:
                        session = boto3.Session(
                            profile_name=attribute['ProfileName'],
                            region_name=region_name
                        )

                        ec2_client = session.client('ec2')

                        response = ec2_client.describe_route_tables(
                            Filters=[
                                {
                                    'Name': 'vpc-id',
                                    'Values': [
                                        vpc,
                                    ]
                                }
                            ]
                        )

                        for route_table in response['RouteTables']:
                            route_table_dict = route_table
                            resource = route_table_dict['RouteTableId']

                            log.debug("Attempting to delete %s from %s - dry-run: %s", resource, vpc, dry_run)
                            response = ec2_client.delete_route_table(
                                RouteTableId=resource,
                                DryRun=dry_run
                            )

                    except ClientError as e:
                        if e.response['Error']['Code'] == 'InvalidClientTokenId':
                            log.warn(
                                "The keypair associated with profile %s is not currently able to authenticate against AWS EC2. Please investigate or remove and rerun.",
                                profile
                            )

                        else:
                            log.warn("Unhandled exception occurred: %s", e)
                            continue


def vpc(inventory, dry_run):
    log = logger.create_logger()

    summary = []

    for account, attribute in inventory.items():

        account_summary = {'AccountId':account}
        vpcs_removed = []

        for region in attribute['Regions']:
            for key, value in region.items():
                region_name = key
                vpc = value['DefaultVpc']

                if not value['NetworkInterfacesPresent'] and not value['Whitelist']:

                    try:
                        session = boto3.Session(
                            profile_name=attribute['ProfileName'],
                            region_name=region_name
                        )

                        ec2_client = session.client('ec2')

                        log.debug("Attempting to delete %s - dry-run: %s", vpc, dry_run)
                        ec2_client.delete_vpc(
                            VpcId=vpc,
                            DryRun=dry_run
                        )

                    except ClientError as e:
                        if e.response['Error']['Code'] == 'InvalidClientTokenId':
                            log.warn(
                                "The keypair associated with profile %s is not currently able to authenticate against AWS EC2. Please investigate or remove and rerun.",
                                profile
                            )

                        else:
                            log.warn("Unhandled exception occurred: %s", e)
                            vpcs_removed.append(vpc)
                            continue

                    vpcs_removed.append(vpc)

        account_summary['VpcsRemoved'] = vpcs_removed
        summary.append(account_summary)

    log.info("Summary: %s", summary)

