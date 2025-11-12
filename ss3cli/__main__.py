import argparse
import configparser
import os
from pathlib import Path
from .s3_client import S3Client
from .cli.ls import add_ls_parser
from .cli.cp import add_cp_parser
from .cli.rm import add_rm_parser
from .cli.presign import add_presign_parser

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="A simple S3 CLI for S3-compatible storage.")

    # Config file and profile arguments
    default_config_path = Path.home() / ".s3" / "config"
    parser.add_argument("--config", help=f"Path to the config file (default: {default_config_path})", default=str(default_config_path))
    parser.add_argument("--profile", help="Profile to use from the config file", default="default")

    # Connection arguments
    parser.add_argument("--endpoint-url", help="S3 endpoint URL")
    parser.add_argument("--access-key", help="S3 access key ID")
    parser.add_argument("--secret-key", help="S3 secret access key")
    parser.add_argument("--region", help="S3 region")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add command parsers
    add_ls_parser(subparsers)
    add_cp_parser(subparsers)
    add_rm_parser(subparsers)
    add_presign_parser(subparsers)

    args = parser.parse_args()

    # Load config from file
    config = configparser.ConfigParser()
    config.read(args.config)

    # Determine credentials
    profile_config = config[args.profile] if args.profile in config else {}

    endpoint_url = args.endpoint_url or os.environ.get('S3_ENDPOINT') or profile_config.get("endpoint_url")
    access_key = args.access_key or os.environ.get('S3_ACCESS_KEY_ID') or profile_config.get("aws_access_key_id")
    secret_key = args.secret_key or os.environ.get('S3_SECRET_ACCESS_KEY') or profile_config.get("aws_secret_access_key")
    region = args.region or os.environ.get('S3_REGION') or profile_config.get("region")

    if not all([endpoint_url, access_key, secret_key, region]):
        print("Error: Endpoint, access key, secret key, and region must be provided.")
        parser.print_help()
        return

    # Create S3 client and execute command
    s3_client = S3Client(endpoint_url, access_key, secret_key, region)
    args.func(s3_client, args)

if __name__ == "__main__":
    main()
