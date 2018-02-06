# default-vpc-killer

Python tool to find and delete all unused default VPC's from all accounts found in ~/.aws/credentials.
If any EC2 instances, security groups, or additional subnets are found, it will skip that VPC.

If a region is included in the whitelist, it will be skipped. 
