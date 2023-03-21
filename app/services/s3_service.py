import os
import boto3

environment = os.getenv("ENVIRONMENT")


class S3Service:
    def __init__(self, bucket=environment):
        self.endpoint = os.getenv("STORE_URL")
        self.access_key = os.getenv("STORE_ACCESS_KEY")
        self.secret_key = os.getenv("STORE_SECRET_KEY")
        self.bucket = bucket

        self.s3 = None

        if environment == "development":
            self.s3 = boto3.resource(service_name='s3',
                                     endpoint_url=self.endpoint,
                                     aws_access_key_id=self.access_key,
                                     aws_secret_access_key=self.secret_key,
                                     region_name="us-east-1").Bucket(self.bucket)
        else:
            self.s3 = boto3.resource(service_name='s3',
                                     aws_access_key_id=self.access_key,
                                     aws_secret_access_key=self.secret_key,
                                     region_name="us-east-1").Bucket(self.bucket)

    def upload_file(self, local_path, filename):
        s3_path = filename
        self.s3.upload_file(local_path, s3_path)
        return True

    def remove_local_file(self, local_path):
        if os.path.exists(local_path):
            os.remove(local_path)
        else:
            print("FILE DOES NOT EXIST")

    def create_directory(self, path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as exc:
                raise exc

    def download_file(self, local_path, filename):
        self.s3.download_file(filename, local_path)

        return True
