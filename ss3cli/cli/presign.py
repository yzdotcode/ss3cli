from ..s3_client import parse_s3_path

def add_presign_parser(subparsers):
    presign_parser = subparsers.add_parser("presign", help="Generate a presigned URL for an S3 object")
    presign_parser.add_argument("s3_path", help="S3 path to the object (e.g., 's3://bucket/file')")
    presign_parser.add_argument("--expires-in", type=int, default=3600, help="Expiration time in seconds (default: 3600)")
    presign_parser.set_defaults(func=execute_presign)

def execute_presign(s3_client, args):
    """Generates a presigned URL for an S3 object."""
    try:
        bucket, key = parse_s3_path(args.s3_path)
        if not key:
            print("Error: Please specify a key to presign.")
            return

        url = s3_client.generate_presigned_url(bucket, key, args.expires_in)
        print(f"\nPresigned URL (expires in {args.expires_in} seconds):\n")
        print(url)
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
