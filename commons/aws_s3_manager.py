import boto3
from dotenv import dotenv_values

# load env variables from .env file
config = dotenv_values(".env")

# get bucket name
bucket_name = config["BUCKET_NAME"]

# create s3 object with all necessary information
s3 = boto3.resource(
    service_name="s3",
    region_name="ap-southeast-1",
    aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"]
)

# get the target bucket
bucket = s3.Bucket(bucket_name)


def upload_file(local_path: str, key: str) -> None:
    """ Upload local file to s3
    Args:
        local_path (String) : Path to the local file
        key (String): File name in the s3 bucket
    """

    bucket.upload_file(Filename=local_path, Key=key)


def delete_file(Key) -> None:
    """Delete file
    Args:
        Key (String): File's name or Key that we want to delete from bucket
    """
    bucket.Object(Key).delete()


def download(file_name: str, local_path: str) -> str:
    """Download file from s3 and save to local

    Args:
        file_name (String): the name of file in s3 bucket
        local_path (String): local path of the file after download

    Returns:
        str: local path of the file after download complete
    """
    bucket.download_file(file_name, local_path)
    return local_path


def get_all_file() -> list:
    """Get all files from s3

    Returns:
        list: all file name from s3 bucket
    """
    list_files = []
    for f in bucket.objects.all():
        list_files.append(f.key)
    return list_files
