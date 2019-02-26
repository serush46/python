# Python Scripts

### 1. AWS Tagging 
Filename: singleexcel.py

This script will allow you to check and list specific tags associated with the resources(AWS Services) and save it in an Excel file and send as a mail.

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
To get help: 
$ python3 singleexcel.py -h
Example:
$ python3 singleexcel.py -r 'ap-south-1'
```
Filename: credentials
This file contains the AWS Keys for sending mail using AWS SES. Please configure the same to send the mail to respective people.

###### NOTE: Things to be modified are listed down below:
- AWS Keys in the script
- AWS Keys and region in the credentials file to send e-mail
- Subject of the mail in the script
- 'From' and 'To' Addresses in the script
