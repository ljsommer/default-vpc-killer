#!/usr/bin/python

import ec2
import local
import logger
import sts
import whitelist

'''
Development:
    Add identification of available regions to profile; don't assume that all profiles have EC2 access to all regions
    Make this pep8 compliant - 80 characters....yeesh
'''


def main():
    log = logger.create_logger()
    log.info("Default VPC killer: Start")

    global account_inventory
    account_inventory = {}

    local.profiles(account_inventory)
    regions = ec2.describe_regions(account_inventory)
    ec2.describe_default_vpcs(account_inventory, regions)
    whitelist.decorate(account_inventory)

    # At this point, we need take no further action if the region is whitelisted
    #sts.account_id(account_inventory)
    #ec2.instances(account_inventory)
    #ec2.subnets(account_inventory)

    log.info("Account inventory for debugging: %s", account_inventory)

main()
