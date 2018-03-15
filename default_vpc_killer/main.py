#!/usr/bin/python
"""
Delete all unused default VPCs in AWS accounts
"""
import os
import ec2
import local
import logger
import sts
import whitelist

'''
Development:
    Add identification of available regions to profile;
    don't assume that all profiles have EC2 access to all regions

    Make this pep8 compliant - 80 characters....yeesh
'''


def main():
    """Main entry point"""
    log = logger.create_logger()
    dry_run = os.environ['dry_run']

    def str_to_bool(string):
        """Convert string to boolean"""
        if string == 'True':
            return True
        elif string == 'False':
            return False

    dry_run = str_to_bool(dry_run)

    log.info("Default VPC killer: Start")
    if dry_run:
        log.info("Dry run flag enabled - no delete operations will occur.")

    account_inventory = {}

    profiles = local.profiles()
    regions = ec2.describe_regions(profiles)

    # Account inventory assembly begins
    sts.account_id(account_inventory, profiles)
    ec2.describe_default_vpcs(account_inventory, regions)
    whitelist.decorate(account_inventory, regions)

    ec2.network_interfaces(account_inventory)

    ec2.subnets(account_inventory, dry_run)
    ec2.internet_gateways(account_inventory, dry_run)
    ec2.vpc(account_inventory, dry_run)


main()
