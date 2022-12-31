# Import the NumPy library as np
import numpy as np
import boto3
from fedasync_core.commons.config import ServerConfig


class AwsS3:

    def __init__(self):
        # get server_tmp folder from config file
        self.tmp = ServerConfig.TMP_FOLDER

        # get bucket name
        self.bucket_name = ServerConfig.BUCKET_NAME

        # create s3 object with all necessary information
        self.s3 = boto3.resource(
            service_name="s3",
            region_name="ap-southeast-1",
            aws_access_key_id=ServerConfig.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=ServerConfig.AWS_SECRET_ACCESS_KEY
        )

        # get the target bucket
        self.bucket = self.s3.Bucket(self.bucket_name)

    def upload_file_to_awss3(self, file_name: str) -> None:
        """ Upload local file to s3
        Args:
            file_name (String) : Path to the local file
        """
        local_path = self.tmp + file_name
        self.bucket.upload_file(Filename=local_path, Key=file_name)

    def delete_awss3_file(self, Key) -> None:
        """Delete file
        Args:
            Key (String): File's name or Key that we want to delete from bucket
        """
        self.bucket.Object(Key).delete()

    def download_awss3_file(self, file_name: str) -> str:
        """Download file from s3 and save to local

        Args:
            file_name (String): the name of file in s3 bucket

        Returns:
            str: local path of the file after download complete
        """
        local_path = self.tmp + file_name
        self.bucket.download_file(file_name, local_path)
        return local_path

    def get_all_awss3_file(self) -> list:
        """Get all files from s3

        Returns:
            list: all file name from s3 bucket
        """
        list_files = []
        for f in self.bucket.objects.all():
            list_files.append(f.key)
        return list_files

