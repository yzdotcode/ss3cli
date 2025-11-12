from ..s3_client import parse_s3_path
from pathlib import Path
import os

def add_cp_parser(subparsers):
    cp_parser = subparsers.add_parser("cp", help="Copy files to and from S3")
    cp_parser.add_argument("source", help="Source path (e.g., 's3://bucket/file' or '/local/file')")
    cp_parser.add_argument("destination", help="Destination path (e.g., 's3://bucket/file' or '/local/file')")
    cp_parser.add_argument("-y", "--yes", action="store_true", help="Skip interactive prompts")
    cp_parser.add_argument("-r", "--recursive", action="store_true", help="Copy directories recursively")
    cp_parser.set_defaults(func=execute_cp)

def execute_cp(s3_client, args):
    if args.recursive:
        copy_recursive(s3_client, args.source, args.destination, args.yes)
    else:
        copy_file(s3_client, args.source, args.destination, args.yes)

def copy_file(s3_client, source, destination, yes):
    """Copies a file to or from S3."""
    try:
        if source.startswith("s3://"):
            bucket, key = parse_s3_path(source)
            download_file(s3_client, bucket, key, destination, yes)
        elif destination.startswith("s3://"):
            bucket, key = parse_s3_path(destination)
            upload_file(s3_client, source, bucket, key, yes)
        else:
            print("Error: One of the paths must be an S3 path (e.g., 's3://bucket/file').")
    except ValueError as e:
        print(f"Error: {e}")

def upload_file(s3_client, local_path, bucket, key, yes):
    """Uploads a file to S3."""
    local_path = Path(local_path)
    if not local_path.is_file():
        print(f"Error: {local_path} is not a valid file.")
        return

    if key.endswith('/'):
        key += local_path.name
        if not yes:
            confirm = input(f"Target is a folder. Upload as '{key}'? (y/n): ").lower()
            if confirm != 'y':
                print("Upload cancelled.")
                return

    try:
        s3_client.upload_file(str(local_path), bucket, key)
    except Exception as e:
        print(f"Error uploading file: {e}")

def download_file(s3_client, bucket, key, local_path, yes):
    """Downloads a file from S3."""
    local_path = Path(local_path)
    if local_path.is_dir():
        local_path = local_path / Path(key).name

    if local_path.exists() and not yes:
        confirm = input(f"File '{local_path}' already exists. Overwrite? (y/n): ").lower()
        if confirm != 'y':
            print("Download cancelled.")
            return

    try:
        s3_client.download_file(bucket, key, str(local_path))
    except Exception as e:
        print(f"Error downloading file: {e}")

def copy_recursive(s3_client, source, destination, yes):
    """Recursively copies files and directories."""
    if source.startswith("s3://"):
        # Recursive download
        bucket, key_prefix = parse_s3_path(source)
        destination_path = Path(destination)

        if destination_path.exists() and not destination_path.is_dir():
            print(f"Error: Destination '{destination}' exists and is not a directory.")
            return

        if not yes and destination_path.is_dir() and any(destination_path.iterdir()):
             confirm = input(f"Destination '{destination}' is not empty. Do you want to merge/overwrite files? (y/n): ").lower()
             if confirm != 'y':
                 print("Download cancelled.")
                 return

        destination_path.mkdir(parents=True, exist_ok=True)

        failed_downloads = []
        successful_downloads = 0

        pages = s3_client.list_objects(bucket, key_prefix, True)

        for page in pages:
            if "Contents" in page and page['Contents'] is not None:
                for obj in page["Contents"]:
                    s3_key = obj["Key"]
                    relative_key = Path(s3_key).relative_to(key_prefix)
                    local_file_path = destination_path / relative_key

                    if s3_key.endswith('/'):
                        continue

                    local_file_path.parent.mkdir(parents=True, exist_ok=True)
                    print(f"copy: s3://{bucket}/{s3_key} to {local_file_path}")

                    try:
                        s3_client.download_file(bucket, s3_key, str(local_file_path))
                        successful_downloads += 1
                    except Exception as e:
                        print(f"  Error downloading {s3_key}: {e}")
                        failed_downloads.append(s3_key)

        print(f"\n{successful_downloads} files copied successfully.")
        if failed_downloads:
            print(f"{len(failed_downloads)} files failed to download:")
            for f in failed_downloads:
                print(f"  - s3://{bucket}/{f}")

    elif destination.startswith("s3://"):
        # Recursive upload
        bucket, key_prefix = parse_s3_path(destination)
        source_path = Path(source)

        if not source_path.is_dir():
            print(f"Error: '{source}' is not a directory.")
            return

        if not yes:
            response = s3_client.list_objects_v2(Bucket=bucket, Prefix=key_prefix, MaxKeys=1)
            if 'Contents' in response and response['Contents']:
                confirm = input(f"Destination 's3://{bucket}/{key_prefix}' is not empty. Do you want to merge/overwrite files? (y/n): ").lower()
                if confirm != 'y':
                    print("Upload cancelled.")
                    return

        failed_uploads = []
        successful_uploads = 0

        for root, _, files in os.walk(source):
            for filename in files:
                local_path = Path(root) / filename
                relative_path = local_path.relative_to(source_path)
                s3_key = str(Path(key_prefix) / relative_path).replace("\\\\", "/")

                print(f"copy: {local_path} to s3://{bucket}/{s3_key}")
                try:
                    s3_client.upload_file(str(local_path), bucket, s3_key)
                    successful_uploads += 1
                except Exception as e:
                    print(f"  Error uploading {local_path}: {e}")
                    failed_uploads.append(str(local_path))

        print(f"\n{successful_uploads} files copied successfully.")
        if failed_uploads:
            print(f"{len(failed_uploads)} files failed to upload:")
            for f in failed_uploads:
                print(f"  - {f}")

    else:
        print("Error: One of the paths must be an S3 path (e.g., 's3://bucket/file').")
