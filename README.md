# Python Scripts

### 1. AWS Tagging 
Filename: singleexcel.py

This script will allow you to check and list specific tags associated with the resources(AWS Services).

Resources used here:
- EC2:
  - Instances
  - AMI
  - Security Group
  - ENI
- EBS:
   - Volume
   - Snapshot
- RDS:
   - Snapshot
   - Instances
- VPC:
   - VPCID
   - SubnetID

#### Pre-requisites and Modules Required!
Install the dependencies
> Python3
> pip3
> boto3
> configparser
> sys
> os
> csv
> smtplib
> logging
> argparse

Provide the region name to execute the script.

```
Help: python3 singleexcel.py -h
Example: python3 singleexcel.py -r 'ap-south-1'
```
