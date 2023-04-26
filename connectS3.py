import boto3
from botocore.exceptions import NoCredentialsError
from cloudpathlib import CloudPath


ACCESS_KEY = 'AKIATPW7Y2BPGCB4NHHD'
SECRET_KEY = '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'


def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False
    


def download_from_aws(s3_file, bucket, local_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    
    try:
        s3.download_file(bucket, s3_file, local_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False
        

    