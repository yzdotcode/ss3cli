from ..s3_client import parse_s3_path

def add_ls_parser(subparsers):
    ls_parser = subparsers.add_parser("ls", help="List S3 buckets or objects")
    ls_parser.add_argument("s3_path", nargs='?', help="S3 path to list objects (e.g., 's3://bucket/path/')")
    ls_parser.add_argument("-r", "--recursive", action="store_true", help="List objects recursively")
    ls_parser.set_defaults(func=execute_ls)

def execute_ls(s3_client, args):
    if args.s3_path:
        try:
            bucket, prefix = parse_s3_path(args.s3_path)
            if not prefix.endswith('/') and prefix != '':
                prefix += '/'

            pages = s3_client.list_objects(bucket, prefix, args.recursive)

            for page in pages:
                if "CommonPrefixes" in page and page['CommonPrefixes'] is not None:
                    for common_prefix in page["CommonPrefixes"]:
                        print(f"                           PRE {common_prefix['Prefix']}")
                if "Contents" in page and page['Contents'] is not None:
                    for obj in page["Contents"]:
                        if obj['Key'] != prefix: # Don't list the "folder" itself
                            print(f"{obj['LastModified']}   {obj['Size']:>10}   {obj['Key']}")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    else:
        try:
            response = s3_client.list_buckets()
            print("Buckets:")
            for bucket in response["Buckets"]:
                print(f"  {bucket['Name']}")
        except Exception as e:
            print(f"Error: {e}")
