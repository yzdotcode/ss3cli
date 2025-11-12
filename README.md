# Simple S3 CLI

A simple command-line interface for interacting with S3-compatible services. It features progress bars for uploads and downloads.

## Prerequisites

- Python 3
- S3 credentials

## Installation

Install directly from a Git repository:

```bash
pip install git+https://github.com/yzdotcode/ss3cli.git
```

## Configuration

The CLI loads credentials in the following order of precedence:

1.  **Command-line arguments:** (`--endpoint-url`, `--access-key`, etc.)
2.  **Environment variables:** (`S3_ENDPOINT`, `S3_ACCESS_KEY_ID`, etc.)
3.  **Configuration file:** (default: `~/.s3/config`)

### Configuration File

You can create a configuration file to store profiles for different S3 services. By default, the CLI looks for `~/.s3/config`.

See [`config.ini.example`](config.ini.example) for the format.

**Note:** This CLI is configured to use AWS Signature Version 4 (`s3v4`), which is required by most modern S3-compatible services.

All commands are now run through the `ss3` executable.

### Listing Buckets and Objects

The `ls` command allows you to list buckets or objects.

**List all buckets:**

```bash
ss3 ls
```

**List objects in a "folder":**

```bash
ss3 ls s3://your-bucket/path/to/folder/
```

**Recursively list objects:**

```bash
ss3 ls -r s3://your-bucket/path/to/folder/
```

### Copying Files

The `cp` command allows you to upload and download files.

**Upload a file:**

```bash
ss3 cp /path/to/local/file.txt s3://your-bucket/
```

If the destination is a "folder" (ends with a `/`), you will be prompted for confirmation. Use the `-y` flag to skip this check.

**Download a file:**

```bash
ss3 cp s3://your-bucket/path/to/file.txt /path/to/local/
```

If the local file already exists, you will be prompted before overwriting. Use the `-y` flag to skip this check.

### Recursive Copy

Use the `-r` or `--recursive` flag to copy directories.

**Upload a directory:**

```bash
ss3 cp -r /path/to/local/dir s3://your-bucket/destination/
```

**Download a "folder":**

```bash
ss3 cp -r s3://your-bucket/path/to/folder /local/destination/
```

If the destination is not empty, you will be prompted before merging/overwriting files. Use the `-y` flag to skip this check.

### Deleting Objects

The `rm` command allows you to delete S3 objects.

**Delete a single object:**

```bash
ss3 rm s3://your-bucket/path/to/file.txt
```

You will be prompted for confirmation. Use the `-y` flag to skip this check.

**Recursively delete objects:**

```bash
ss3 rm -r s3://your-bucket/path/to/folder/
```

You will be prompted with a count of the objects to be deleted. Use the `-y` flag to skip this check.

### Generating Presigned URLs

The `presign` command generates a temporary, shareable URL for a private object.

```bash
ss3 presign s3://your-bucket/path/to/file.txt
```

You can customize the expiration time (in seconds) with the `--expires-in` flag:

```bash
ss3 presign s3://your-bucket/path/to/file.txt --expires-in 60
```

### Using a Profile from the Config File

```bash
# This will use the [my-profile] section of your config file
ss3 --profile my-profile ls
```

### Using Environment Variables

```bash
export S3_ENDPOINT="<your-s3-endpoint-url>"
export S3_ACCESS_KEY_ID="<your-access-key>"
export S3_SECRET_ACCESS_KEY="<your-secret-key>"
export S3_REGION="<your-region>"

ss3 ls
```

### Using Command-Line Arguments

```bash
ss3 --endpoint-url <your-s3-endpoint-url> --access-key <your-access-key> --secret-key <your-secret-key> --region <your-region> ls
```
