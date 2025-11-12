from ..s3_client import parse_s3_path

def add_rm_parser(subparsers):
    rm_parser = subparsers.add_parser("rm", help="Delete S3 objects")
    rm_parser.add_argument("s3_path", help="S3 path to the object or prefix to delete (e.g., 's3://bucket/file')")
    rm_parser.add_argument("-r", "--recursive", action="store_true", help="Delete objects recursively")
    rm_parser.add_argument("-y", "--yes", action="store_true", help="Skip interactive prompts")
    rm_parser.set_defaults(func=execute_rm)

def execute_rm(s3_client, args):
    if args.recursive:
        # Recursive delete
        try:
            bucket, key_prefix = parse_s3_path(args.s3_path)
            if not key_prefix:
                print("Error: Recursive delete on a whole bucket is not supported. Please specify a prefix.")
                return

            pages = s3_client.list_objects(bucket, key_prefix, True)

            objects_to_delete = []
            for page in pages:
                if "Contents" in page and page['Contents'] is not None:
                    for obj in page["Contents"]:
                        objects_to_delete.append({'Key': obj['Key']})

            if not objects_to_delete:
                print(f"No objects found under 's3://{bucket}/{key_prefix}'.")
                return

            if not args.yes:
                confirm = input(f"Found {len(objects_to_delete)} objects under 's3://{bucket}/{key_prefix}'. Are you sure you want to delete them? (y/n): ").lower()
                if confirm != 'y':
                    print("Deletion cancelled.")
                    return

            for i in range(0, len(objects_to_delete), 1000):
                chunk = objects_to_delete[i:i + 1000]
                print(f"Deleting {len(chunk)} objects...")
                response = s3_client.delete_objects(bucket, chunk)
                if 'Errors' in response and response['Errors']:
                    for error in response['Errors']:
                        print(f"  Error deleting {error['Key']}: {error['Message']}")

            print(f"Deletion of objects under 's3://{bucket}/{key_prefix}' complete.")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    else:
        # Single object delete
        try:
            bucket, key = parse_s3_path(args.s3_path)
            if not key:
                print("Error: Deleting a bucket is not supported. Please specify a key.")
                return

            if not args.yes:
                confirm = input(f"Are you sure you want to delete 's3://{bucket}/{key}'? (y/n): ").lower()
                if confirm != 'y':
                    print("Deletion cancelled.")
                    return

            print(f"Deleting s3://{bucket}/{key}...")
            s3_client.delete_object(bucket, key)
            print("Delete complete.")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error deleting object: {e}")
