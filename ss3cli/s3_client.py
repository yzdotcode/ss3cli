import boto3
import re
import threading
from pathlib import Path
from tqdm import tqdm

class ProgressPercentage(object):
    def __init__(self, filename, size):
        self._filename = filename
        self._size = size
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self._tqdm = tqdm(total=size, unit='B', unit_scale=True, desc=self._filename)

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            self._tqdm.update(bytes_amount)

    def __del__(self):
        self._tqdm.close()

def parse_s3_path(s3_path):
    """Parses an S3 path into a bucket and key."""
    match = re.match(r"s3://([^/]+)/?(.*)", s3_path)
    if not match:
        raise ValueError(f"Invalid S3 path: {s3_path}")
    return match.groups()

from botocore.client import Config

class S3Client:
    def __init__(self, endpoint_url, access_key, secret_key, region):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=Config(signature_version='s3v4')
        )

    def list_buckets(self):
        return self.s3.list_buckets()

    def list_objects(self, bucket, prefix, recursive):
        if recursive:
            paginator = self.s3.get_paginator('list_objects_v2')
            return paginator.paginate(Bucket=bucket, Prefix=prefix)
        else:
            paginator = self.s3.get_paginator('list_objects_v2')
            return paginator.paginate(Bucket=bucket, Prefix=prefix, Delimiter='/')

    def upload_file(self, local_path, bucket, key):
        file_size = Path(local_path).stat().st_size
        progress = ProgressPercentage(Path(local_path).name, file_size)
        self.s3.upload_file(str(local_path), bucket, key, Callback=progress)

    def download_file(self, bucket, key, local_path):
        head_object = self.s3.head_object(Bucket=bucket, Key=key)
        file_size = head_object['ContentLength']
        progress = ProgressPercentage(Path(key).name, file_size)
        self.s3.download_file(bucket, key, str(local_path), Callback=progress)

    def delete_object(self, bucket, key):
        self.s3.delete_object(Bucket=bucket, Key=key)

    def delete_objects(self, bucket, keys):
        return self.s3.delete_objects(Bucket=bucket, Delete={'Objects': keys})

    def list_objects_v2(self, Bucket, Prefix, MaxKeys):
        return self.s3.list_objects_v2(Bucket=Bucket, Prefix=Prefix, MaxKeys=MaxKeys)

    def generate_presigned_url(self, bucket, key, expires_in):
        return self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expires_in
        )
