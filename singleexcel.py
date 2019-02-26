import boto3, logging, sys, argparse, csv, smtplib, os, configparser
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Credentials
ACCESS_KEY=''
SECRET_KEY=''
FAILED_EXIT_CODE = 1

# Enable the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S %Z')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Regions list
Regions = {
'us-east-2':"Ohio(USA)",
'us-east-1':"North Virginia(USA)",
'us-west-1':"North California(USA)",
'us-west-2':"Oregon(USA)",
'ap-south-1':"Mumbai(India)",
'ap-northeast-3': "Osaka(Japan)",
'ap-northeast-2':"Seoul(SouthKorea)",
'ap-southeast-1':"Singapore)",
'ap-southeast-2':"Sydney(Australia)",
'ap-northeast-1':"Tokyo(Japan)",
'ca-central-1':"Central(Canada)",
'cn-north-1':"Beijing(China)",
'cn-northwest-1':"Ningxia(China)",
'eu-central-1':	"Frankfurt(Germany)",
'eu-west-1':"Ireland(UK)",
'eu-west-2':"London(UK)",
'eu-west-3':"Paris(France)",
'eu-north-1':"Stockholm(Sweden)",
'sa-east-1':"São Paulo(Brazil)"
}

# Connect to AWS boto3 Client
def aws_connect_client(service,REGION):
    try:
        # Gaining API session
        session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        # Connect the resource
        conn_client = session.client(service, REGION)
    except Exception as e:
        logger.error('Could not connect to region: %s and resources: %s , Exception: %s\n' % (REGION, service, e))
        conn_client = None
    return conn_client

# Connect to AWS boto3 Resource
def aws_connect_resource(service,REGION):
    try:
        # Gaining API session
        session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        # Connect the resource
        conn_resource = session.resource(service, REGION)
    except Exception as e:
        logger.error('Could not connect to region: %s and resources: %s , Exception: %s\n' % (REGION, service, e))
        conn_resource = None
    return conn_resource

# Get AWS Account ID
def get_aws_account_id(REGION):
    return aws_connect_resource('iam', REGION).CurrentUser().arn.split(':')[4]

# Tag Keys
row = ['Client','Environment','Name','Required','Team','UserName']

# Create CSV File with Headers
header_row = ['Resource', 'ID', 'Client', 'Environment', 'Name', 'Required', 'Team', 'UserName']
with open('Resources.csv', 'w') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(header_row)
csvFile.close()



# Get all EC2 ID's

# def list_ec2_instance_ids(REGION):
#     ec2_client = aws_connect_client('ec2',REGION)
#     try:
#         instance_list = []
#         logger.info('Getting EC2 instance list')
#         response = ec2_client.describe_instances()
#         for reservation in response["Reservations"]:
#             for instance in reservation["Instances"]:
#                 instance_list.append(instance["InstanceId"])
#         instance_list = [id['Instances'][0]['InstanceId'] for id in response['Reservations']]
    # except Exception as e:
    #     logger.info('Error - {}'.format(e))
    # return instance_list



def ec2_instance_details(REGION):
    ec2_client = aws_connect_client('ec2',REGION)
    try:
        ec2_map = {}
        ec2_instance_list = []
        response = ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name','Values': ['pending','running']}])
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                ec2_instance_list.append(instance["InstanceId"])

        # Sort the Key-Value pairs
        logger.info('Appending EC2 Instance Details')
        for x,k in zip(response["Reservations"],ec2_instance_list):
            for i in x["Instances"]:
                ec2_map[i["InstanceId"]] = i
                try:
                    if 'Tags' in i:
                        ec2_tag_key = [id['Key'] for id in i['Tags']]
                        ec2_tag_value = [id['Value'] for id in i['Tags']]
                        convert_to_dict = dict(zip(ec2_tag_key,ec2_tag_value))
                        sorted_dict = (dict(sorted(convert_to_dict.items())))
                    else:
                        logger.info('There is no default Tags for this EC2: {}'.format(k))
                        pass
                except KeyError:
                    logger.info('There is no default Tags for this EC2: {}'.format(k))
                ec2_tag_list = []
                for j in range(0,len(row)):
                    if row[j] in sorted_dict:
                        (ec2_tag_list.append(sorted_dict[row[j]]))
                    else:
                        (ec2_tag_list.append(''))
                ec2_tag_list.insert(0, k)
                ec2_tag_list.insert(0,'EC2')
                # Save the output to CSV
                with open("Resources.csv", "a") as fp:
                    wr = csv.writer(fp, dialect='excel')
                    wr.writerow(ec2_tag_list)
                fp.close()

    except Exception as e:
        logger.error('Error - {}'.format(e))
        sys.exit(FAILED_EXIT_CODE)



# Get all EC2 Snapshot-IDs

# def list_ec2_snap_ids(REGION):
#     ec2_client = aws_connect_client('ec2',REGION)
#     try:
#         logger.info('Fetching EC2 Snapshot IDs')
#         response = ec2_client.describe_snapshots(OwnerIds=[get_aws_account_id(REGION)])
#         ec2_snapshot_list = [id['SnapshotId'] for id in response['Snapshots']]
#     except Exception as e:
#         logger.info('Error - {}'.format(e))
#     return ec2_snapshot_list

# def ec2_snap_details(REGION):
#     ec2_client = aws_connect_client('ec2',REGION)
#     try:
#         pagination = True
#         next_token = ""
#         ec2_snap_list = list_ec2_snap_ids(REGION)
#         if len(ec2_snap_list) >= 400:
#             logger.info("There are hell lot of Snapshots around {}. Meanwhile have a break, while I update the sheet ;) & "
#                         "don't close the session".format(len(ec2_snap_list)))
#         logger.info('Appending EC2Snapshot Details')
#         while pagination:
#             for i in ec2_snap_list:
#                 response = ec2_client.describe_snapshots(Filters=[{'Name': 'snapshot-id', 'Values': [i]}],
#                                                          MaxResults=100, NextToken=next_token)
#                 try:
#                     tags = [id['Tags'] for id in response['Snapshots']]
#                     ec2_snap_tag_key = [id['Key'] for id in tags[0]]
#                     ec2_snap_tag_value = [id['Value'] for id in tags[0]]
#                     convert_to_dict = dict(zip(ec2_snap_tag_key, ec2_snap_tag_value))
#                     sorted_dict = (dict(sorted(convert_to_dict.items())))
#                 except KeyError:
#                     logger.info('There is no default Tags for this EC2-Snapshot: {}'.format(i))
#                 ec2_snapshot_list = []
#                 for j in range(0, len(row)):
#                     if row[j] in sorted_dict:
#                         (ec2_snapshot_list.append(sorted_dict[row[j]]))
#                     else:
#                         (ec2_snapshot_list.append(''))
#                 ec2_snapshot_list.insert(0, i)
#                 ec2_snapshot_list.insert(0, 'EC2Snapshot')
                # Save the output to CSV
                # with open("Resources.csv", "a") as fp:
                #     wr = csv.writer(fp, dialect='excel')
                #     wr.writerow(ec2_snapshot_list)
                # fp.close()
                # if 'NextToken' in response:
                #     next_token = response["NextToken"]
                #     pagination = True
                # else:
                #     pagination = False
    # except Exception as e:
    #     logger.info('Error - {}'.format(e))
    #     sys.exit(FAILED_EXIT_CODE)


def ec2_snap_details(REGION):
    ec2_client = aws_connect_client('ec2',REGION)
    try:
        ec2_snapshot_map = {}
        response = ec2_client.describe_snapshots(OwnerIds=[get_aws_account_id(REGION)])
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            ec2_snap_list = [id['SnapshotId'] for id in response['Snapshots']]
            if len(ec2_snap_list) >= 400:
                logger.info("There are hell lot of Snapshots around {}. Meanwhile have a break, while I update the sheet ;) & "
                        "don't close the session".format(len(ec2_snap_list)))
            logger.info('Appending EC2Snapshot Details')
            for i,k in zip(response['Snapshots'],ec2_snap_list):
                ec2_snapshot_map[i["SnapshotId"]] = i

                if 'Tags' in i:
                    snap_tag_key = [id['Key'] for id in i['Tags']]
                    snap_tag_value = [id['Value'] for id in i['Tags']]
                    convert_to_dict = dict(zip(snap_tag_key, snap_tag_value))
                    sorted_dict = (dict(sorted(convert_to_dict.items())))
                else:
                    logger.info("There's no Tags for the Snapshot: {}".format(i['SnapshotId']))
                    pass
                snap_list = []
                for j in range(0,len(row)):
                    if row[j] in sorted_dict:
                        (snap_list.append(sorted_dict[row[j]]))
                    else:
                        (snap_list.append(''))
                snap_list.insert(0,k)
                snap_list.insert(0,'EC2Snapshot')
                # Save the output to CSV
                with open("Resources.csv", "a") as fp:
                    wr = csv.writer(fp, dialect='excel')
                    wr.writerow(snap_list)
                fp.close()
        else:
            sys.exit(FAILED_EXIT_CODE)
    except Exception as e:
        logger.info('Error - {}'.format(e))
        sys.exit(FAILED_EXIT_CODE)



# def list_ami_ids(REGION):
#     ec2_client = aws_connect_client('ec2',REGION)
#     try:
#         logger.info("Fetching AMI IDs")
#         response = ec2_client.describe_images(Owners=[get_aws_account_id(REGION)])
#         # Get Image Map
#         image_map = {}
#         for images in response["Images"]:
#             image_map[images["ImageId"]] = images
#         # Get all Image IDs
#         image_list = [id['ImageId'] for id in response['Images']]
#     except Exception as e:
#         logger.info("Not able to list the AMI ID's, Error - {}".format(e))
#     return image_map, image_list



# Get all AMI ID's
def ami_details(REGION):
    ec2_client = aws_connect_client('ec2',REGION)
    try:
        logger.info('Appending AMI Details')
        image_map = {}
        # Sort the Key-Value pairs
        response = ec2_client.describe_images(Owners=[get_aws_account_id(REGION)])
        image_list = [id['ImageId'] for id in response['Images']]
        for i,k in zip(response["Images"],image_list):
            image_map[i["ImageId"]] = i
            if 'Tags' in i:
                ami_tag_key = [id['Key'] for id in i['Tags']]
                ami_tag_value = [id['Value'] for id in i['Tags']]
                convert_to_dict = dict(zip(ami_tag_key, ami_tag_value))
                sorted_dict = (dict(sorted(convert_to_dict.items())))
            else:
                logger.info("There's no Tags for the AMI: {}".format(i['ImageId']))
                pass
            ami_tag_list = []
            for j in range(0,len(row)):
                if row[j] in sorted_dict:
                    (ami_tag_list.append(sorted_dict[row[j]]))
                else:
                    (ami_tag_list.append(''))
            ami_tag_list.insert(0,k)
            ami_tag_list.insert(0,'AMI')
            # Save the output to CSV
            with open("Resources.csv", "a") as fp:
                wr = csv.writer(fp, dialect='excel')
                wr.writerow(ami_tag_list)
            fp.close()
    except Exception as e:
        logger.error('Error: {}'.format(e))
        sys.exit(FAILED_EXIT_CODE)


# Get all Security Group ID's
def list_sg_ids(REGION):
    ec2_client = aws_connect_client('ec2',REGION)
    try:
        logger.info('Fetching SecurityGroup IDs')
        response = ec2_client.describe_security_groups()
        sg_list = [id['GroupId'] for id in response['SecurityGroups']]
    except Exception as e:
        logger.info("Not able to list the AMI-ID's, Error: {}".format(e))
    return sg_list


def sg_details(REGION):
    ec2_client = aws_connect_client('ec2',REGION)
    pagination = True
    next_token = ""
    try:
        sg_list = list_sg_ids(REGION)
        # Sort the Key-Value pairs
        logger.info('Appending SecurityGroups Details')
        while pagination:
            for i in sg_list:
                response = ec2_client.describe_security_groups(Filters=[{'Name': 'group-id','Values': [i]}],MaxResults=200, NextToken=next_token)
                try:
                    tags = [id['Tags'] for id in response['SecurityGroups']]
                    sg_tag_key = [id['Key'] for id in tags[0]]
                    sg_tag_value = [id['Value'] for id in tags[0]]
                    convert_to_dict = dict(zip(sg_tag_key,sg_tag_value))
                    sorted_dict = (dict(sorted(convert_to_dict.items())))
                except KeyError:
                    logger.info ('There is no Tags for SG: {}'.format(i))
                    sorted_dict = {'Empty': ''}
                sg_tag_list = []
                for j in range(0,len(row)):
                    if row[j] in sorted_dict:
                        (sg_tag_list.append(sorted_dict[row[j]]))
                    else:
                        sg_tag_list.append('')
                sg_tag_list.insert(0,i)
                sg_tag_list.insert(0,'SG')
                # Save the output to CSV
                with open("Resources.csv", "a") as fp:
                    wr = csv.writer(fp, dialect='excel')
                    wr.writerow(sg_tag_list)
                fp.close()
                if 'NextToken' in response:
                    next_token = response["NextToken"]
                    pagination = True
                else:
                    pagination = False
    except Exception as e:
        logger.error("Neither filter SecurityGroupIDs nor update SecurityGroupIds in CSV, Error - {}".format(e))
        sys.exit(FAILED_EXIT_CODE)

# Get all Network Interface ID's

# def list_eni_ids(REGION):
#     ec2_client = aws_connect_client('ec2',REGION)
#     try:
#         logger.info('Getting ENI Network IDs')
#         response = ec2_client.describe_network_interfaces()
#         nw_list = [id['NetworkInterfaceId'] for id in response['NetworkInterfaces']]
#     except Exception as e:
#         logger.info('Error - {}'.format(e))
#     return nw_list


def nw_details(REGION):
    ec2_client = aws_connect_client('ec2',REGION)
    try:
        nw_map = {}
        response = ec2_client.describe_network_interfaces()
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            nw_list = [id['NetworkInterfaceId'] for id in response['NetworkInterfaces']]
            # Sort the Key-Value pairs
            logger.info('Appending Network Interface Details')
            for x,k in zip(response["NetworkInterfaces"],nw_list):
                nw_map[x["NetworkInterfaceId"]] = x
                if 'TagSet' in x:
                    nw_tag_key = [id['Key'] for id in x['TagSet']]
                    nw_tag_value = [id['Value'] for id in x['TagSet']]
                    convert_to_dict = dict(zip(nw_tag_key,nw_tag_value))
                    sorted_dict = (dict(sorted(convert_to_dict.items())))
                    if sorted_dict == {}:
                        logger.info ('There is no Tags for N/W ID: {}'.format(k))
                eni_tag_list = []
                for j in range(0,len(row)):
                    if row[j] in sorted_dict:
                        (eni_tag_list.append(sorted_dict[row[j]]))
                    else:
                        (eni_tag_list.append(''))
                eni_tag_list.insert(0,k)
                eni_tag_list.insert(0,'ENI')
                # Save the output to CSV
                with open("Resources.csv", "a") as fp:
                    wr = csv.writer(fp, dialect='excel')
                    wr.writerow(eni_tag_list)
                fp.close()
    except Exception as e:
        logger.error("Not able to filter/update N/W IDs, Error: {}".format(e))
        sys.exit(FAILED_EXIT_CODE)

# Get all Volume IDs
def list_volume_ids(REGION):
    ec2_client = aws_connect_client('ec2',REGION)
    try:
        logger.info('Getting All Volume IDs')
        response = ec2_client.describe_volumes()
        vol_list = [id['VolumeId'] for id in response['Volumes']]
    except Exception as e:
        logger.info('Error - {}'.format(e))
    return vol_list


def volume_details(REGION):
    ec2_client = aws_connect_client('ec2',REGION)
    try:
        pagination = True
        next_token = ""
        volume_list = list_volume_ids(REGION)
        if len(volume_list) >= 300:
            logger.info("There are hell lot of Volumes around {}. Meanwhile have a break, while I update the sheet ;) & "
                        "don't close the session".format(len(volume_list)))
        # Sort the Key-Value pairs
        logger.info('Appending Volume Details, HANG ON')
        while pagination:
            for i in volume_list:
                response = ec2_client.describe_volumes(Filters=[{'Name': 'volume-id','Values': [i]}], MaxResults=100, NextToken=next_token)
                try:
                    tags = [id['Tags'] for id in response['Volumes']]
                    vol_tag_key = [id['Key'] for id in tags[0]]
                    vol_tag_value = [id['Value'] for id in tags[0]]
                    convert_to_dict = dict(zip(vol_tag_key,vol_tag_value))
                    sorted_dict = (dict(sorted(convert_to_dict.items())))
                except KeyError:
                    logger.info ('There is no Tags for this Volume: {}'.format(i))
                    sorted_dict = {'Empty': ''}
                vol_tag_list = []
                for j in range(0,len(row)):
                    if row[j] in sorted_dict:
                        (vol_tag_list.append(sorted_dict[row[j]]))
                    else:
                        (vol_tag_list.append(''))
                vol_tag_list.insert(0,i)
                vol_tag_list.insert(0,'EBS')
                # Save the output to CSV
                with open("Resources.csv", "a") as fp:
                    wr = csv.writer(fp, dialect='excel')
                    wr.writerow(vol_tag_list)
                fp.close()
                if 'NextToken' in response:
                    next_token = response["NextToken"]
                    pagination = True
                else:
                    pagination = False
    except Exception as e:
        logger.error("Neither filter VolumeIDs nor update VolumeIDs in CSV, Error: {}".format(e))
        sys.exit(FAILED_EXIT_CODE)


# Get all VPC IDs
def list_vpc_ids(REGION):
    ec2_client = aws_connect_client('ec2',REGION)
    try:
        logger.info('Getting All VPC IDs')
        response = ec2_client.describe_vpcs()
        vpc_list = [id['VpcId'] for id in response['Vpcs']]
    except Exception as e:
        logger.info('Error - {}'.format(e))
    return vpc_list


def vpc_details(REGION):
    ec2_client = aws_connect_client('ec2',REGION)
    try:
        vpc_list = list_vpc_ids(REGION)
        # Sort the Key-Value pairs
        logger.info('Appending VPC Details')
        for i in vpc_list:
            response = ec2_client.describe_vpcs(VpcIds=[i])
            try:
                tags = [id['Tags'] for id in response['Vpcs']]
                vpc_tag_key = [id['Key'] for id in tags[0]]
                vpc_tag_value = [id['Value'] for id in tags[0]]
                convert_to_dict = dict(zip(vpc_tag_key,vpc_tag_value))
                sorted_dict = (dict(sorted(convert_to_dict.items())))
            except KeyError:
                logger.info ('There is no Tags for this VPC: {}'.format(i))
                sorted_dict = {'Empty': ''}
            vpc_tag_list = []
            for j in range(0,len(row)):
                if row[j] in sorted_dict:
                    (vpc_tag_list.append(sorted_dict[row[j]]))
                else:
                    (vpc_tag_list.append(''))
            vpc_tag_list.insert(0,i)
            vpc_tag_list.insert(0,'VPC')
            # Save the output to CSV
            with open("Resources.csv", "a") as fp:
                wr = csv.writer(fp, dialect='excel')
                wr.writerow(vpc_tag_list)
            fp.close()
    except Exception as e:
        logger.error("Neither filter VPC-IDs nor update VPC-IDs in CSV, Error: {}".format(e))
        sys.exit(FAILED_EXIT_CODE)



# Get all Subnet-IDs

def subnet_details(REGION):
    ec2_client = aws_connect_client('ec2',REGION)
    try:
        subnet_map = {}
        response = ec2_client.describe_subnets()
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            logger.info('Obtaining all Subnet IDs')
            subnet_ids_list = [id['SubnetId'] for id in response['Subnets']]
            if len(subnet_ids_list) >= 100:
                    logger.info("There are lot of Subnets around {}. Meanwhile have a break, while I update the sheet ;) & "
                                "don't close the session".format(len(subnet_ids_list)))
            logger.info('Appending Subnet Details')
            try:
                for i,k in zip(response['Subnets'],subnet_ids_list):
                    subnet_map[i["SubnetId"]] = i
                    if 'Tags' in i:
                        subnet_tag_key = [id['Key'] for id in i['Tags']]
                        subnet_tag_value = [id['Value'] for id in i['Tags']]
                        convert_to_dict = dict(zip(subnet_tag_key,subnet_tag_value))
                        sorted_dict = (dict(sorted(convert_to_dict.items())))
                        sub_tag_list = []
                        for j in range(0, len(row)):
                            if row[j] in sorted_dict:
                                (sub_tag_list.append(sorted_dict[row[j]]))
                            else:
                                (sub_tag_list.append(''))
                        sub_tag_list.insert(0, k)
                        sub_tag_list.insert(0, 'Subnet')
                        # Save the output to CSV
                        with open("Resources.csv", "a") as fp:
                            wr = csv.writer(fp, dialect='excel')
                            wr.writerow(sub_tag_list)
                        fp.close()
            except KeyError:
                    logger.info ('There is no Tags for this Subnet: {}'.format(k))

    except Exception as e:
        logger.error("Neither filter Subnet-IDs nor update Subnet-IDs in CSV, Error: {}".format(e))
        sys.exit(FAILED_EXIT_CODE)


# Get all RDS IDs
def list_rds_ids(REGION):
    rds_client = aws_connect_client('rds',REGION)
    try:
        logger.info('Obtaining all RDS IDs')
        response = rds_client.describe_db_instances()
        rds_list = [id['DBInstanceIdentifier'] for id in response['DBInstances']]
    except Exception as e:
        logger.info('Error - {}'.format(e))
    return rds_list


def rds_details(REGION):
    rds_client = aws_connect_client('rds',REGION)
    try:
        rds_list = list_rds_ids(REGION)
        # Sort the Key-Value pairs
        logger.info('Appending RDS Details, Hold tightly')
        for i in rds_list:
            response = rds_client.list_tags_for_resource\
                (ResourceName='arn:aws:rds:{}:{}:db:{}'.format(REGION,get_aws_account_id(REGION),i))
            tags = [id for id in response['TagList']]
            if tags == []:
                logger.info ('There is no Tags for RDS: {}'.format(i))
            rds_tag_key = [id['Key'] for id in tags]
            rds_tag_value = [id['Value'] for id in tags]
            convert_to_dict = dict(zip(rds_tag_key,rds_tag_value))
            sorted_dict = (dict(sorted(convert_to_dict.items())))
            rds_tag_list = []
            for j in range(0,len(row)):
                if row[j] in sorted_dict:
                    (rds_tag_list.append(sorted_dict[row[j]]))
                else:
                    (rds_tag_list.append(''))
            rds_tag_list.insert(0,i)
            rds_tag_list.insert(0,'RDS')
            # Save the output to CSV
            with open("Resources.csv", "a") as fp:
                wr = csv.writer(fp, dialect='excel')
                wr.writerow(rds_tag_list)
            fp.close()
    except Exception as e:
        logger.error("Neither filter RDS nor update RDS-IDs in CSV, Error: {}".format(e))
        sys.exit(FAILED_EXIT_CODE)



# Get all RDS Snapshot-IDs
# def list_rds_snap_ids(REGION):
#     rds_client = aws_connect_client('rds',REGION)
#     try:
#         logger.info('Fetching all RDS Snapshot IDs')
#         pagination = True
#         marker = ""
#         rds_snapshot_list = []
#         while pagination:
#             response = rds_client.describe_db_snapshots(Marker=marker,IncludeShared=True)
#             rds_snap_list = [id['DBSnapshotIdentifier'] for id in response['DBSnapshots']]
#             for snap in rds_snap_list:
#                 rds_snapshot_list.append(snap)
#             if 'Marker' in response:
#                 marker = response["Marker"]
#                 pagination = True
#             else:
#                 pagination = False
#     except Exception as e:
#         logger.info('Error: {}'.format(e))
#     return rds_snapshot_list

# def rds_snap_details(REGION):
#     rds_client = aws_connect_client('rds',REGION)
#     try:
#         rds_snap_list = list_rds_snap_ids(REGION)
#         # Sort the Key-Value pairs
#         logger.info('Appending RDSSnapshot Details, Give me a moment please')
#         for i in rds_snap_list:
#             response = rds_client.list_tags_for_resource\
#                 (ResourceName='arn:aws:rds:{}:{}:snapshot:{}'.format(REGION,get_aws_account_id(REGION),i))
#             time.sleep(1)
#             tags = [id for id in response['TagList']]
#             if tags == []:
#                 logger.info ('There is no Tags for RDSSnapshot: {}'.format(i))
#             rds_tag_key = [id['Key'] for id in tags]
#             rds_tag_value = [id['Value'] for id in tags]
#             convert_to_dict = dict(zip(rds_tag_key,rds_tag_value))
#             sorted_dict = (dict(sorted(convert_to_dict.items())))
#             rds_tag_list = []
#             for j in range(0,len(row)):
#                 if row[j] in sorted_dict:
#                     (rds_tag_list.append(sorted_dict[row[j]]))
#                 else:
#                     (rds_tag_list.append(''))
#             rds_tag_list.insert(0,i)
#             rds_tag_list.insert(0,'RDSSnapshot')
#             # Save the output to CSV
#             with open("Resources.csv", "a") as fp:
#                 wr = csv.writer(fp, dialect='excel')
#                 wr.writerow(rds_tag_list)
#             fp.close()
#     except Exception as e:
#         logger.error("Neither filter RDSSnapshot nor update RDSSnapshot-IDs in CSV, Error : {}".format(e))
#         sys.exit(FAILED_EXIT_CODE)


# Get all RDS Snapshot-IDs
def rds_snap_details(REGION):
    rds_snap_client = aws_connect_client('resourcegroupstaggingapi',REGION)
    try:
        response = rds_snap_client.get_resources(ResourceTypeFilters=['rds:snapshot', 'rds:cluster-snapshot'],ResourcesPerPage=50)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            logger.info('Fetching all RDSSnapshot IDs')
        while response['PaginationToken']:
            response = rds_snap_client.get_resources(ResourceTypeFilters=['rds:snapshot', 'rds:cluster-snapshot'],
                                            ResourcesPerPage=50, PaginationToken=response['PaginationToken'])
            if response['ResourceTagMappingList'] != []:
                for i,k in zip(response['ResourceTagMappingList'], response['ResourceTagMappingList']):
                    if 'Tags' in i:
                        rdssnap_tag_key = [id['Key'] for id in i['Tags']]
                        rdssnap_tag_value = [id['Value'] for id in i['Tags']]
                        convert_to_dict = dict(zip(rdssnap_tag_key, rdssnap_tag_value))
                        sorted_dict = (dict(sorted(convert_to_dict.items())))
                        rdssnap_tag_list = []
                        for j in range(0, len(row)):
                            if row[j] in sorted_dict:
                                (rdssnap_tag_list.append(sorted_dict[row[j]]))
                            else:
                                (rdssnap_tag_list.append(''))
                        id_list = (k['ResourceARN'])
                        reverse_id_list = id_list.rsplit(':', 1)[1]
                        rdssnap_tag_list.insert(0, reverse_id_list)
                        rdssnap_tag_list.insert(0, 'RDSSnapshot')
                        with open("Resources.csv", "a") as fp:
                            wr = csv.writer(fp, dialect='excel')
                            wr.writerow(rdssnap_tag_list)
                        fp.close()
    except Exception as e:
        logger.error("Neither filter RDSSnapshot nor update RDSSnapshot-IDs in CSV, Error : {}".format(e))
        sys.exit(FAILED_EXIT_CODE)

# Send Mail with attachment
def send_mail(REGION):
    try:
        config = configparser.ConfigParser()
        config.read("credentials")
        smtp_server = config.get('settings', 'smtp_server')
        smtp_username = config.get('settings', 'smtp_username')
        smtp_password = config.get('settings', 'smtp_password')
        smtp_port = config.get('settings', 'smtp_port')
        fromaddr = 'test@gmail.com'
        toaddr = 'hello@yahoo.com'
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = ", ".join(toaddr)
        # msg['To'] = toaddr
        msg['Subject'] = " Resources TagList "
        body = "Hi Team, \nPlease find the attachment for Resources with Tag Details for {} region".format(Regions[REGION])
        msg.attach(MIMEText(body, 'plain'))
        # Attach a file
        contentfile = 'Resources.csv'
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(contentfile, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'\
                                            % os.path.basename(contentfile))
        msg.attach(part)
        # Define SMTP server
        server = smtplib.SMTP(
        host = smtp_server,
        port = smtp_port,
        timeout = 10
        )
        server.set_debuglevel(2)
        server.starttls()
        server.ehlo()
        server.login(smtp_username, smtp_password)
        # Send the mail
        server.sendmail(fromaddr, toaddr, msg.as_string())
        server.quit()

    except Exception as e:
        logger.error("Not able to send Mail, Error: {}".format(e))
        sys.exit(FAILED_EXIT_CODE)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AWS Resource Filter Script')
    parser.add_argument('--region', '-r', required=True, help='Specify the region.')
    args = parser.parse_args()

    logger.info('Fetching all the Resources in {} region with the given Tags'.format(Regions[args.region.lower()]))

    # Calling all the main functions
    ec2_instance_details(args.region.lower())
    ec2_snap_details(args.region.lower())
    sg_details(args.region.lower())
    ami_details(args.region.lower())
    nw_details(args.region.lower())
    volume_details(args.region.lower())
    vpc_details(args.region.lower())
    subnet_details(args.region.lower())
    rds_details(args.region.lower())
    rds_snap_details(args.region.lower())
    send_mail(args.region.lower())


