import boto3
from botocore.client import Config
import uuid


BUCKET_NAME = "carecampus"
REGION = "sfo3"

client = boto3.client(
    "s3",
    region_name=REGION,
    endpoint_url="https://sfo3.digitaloceanspaces.com",
    aws_access_key_id="DO00GE36B6DNYDBUGXDY",
    aws_secret_access_key="rw3qyfBfyRqChMMdR0+88py1CTc3H2qmehLz1XiKGEA",
    config=Config(signature_version="s3v4"),
)


def upload_image(file, folder: str):

    extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{extension}"

    key = f"{folder}/{filename}"

    client.upload_fileobj(
        file.file,
        BUCKET_NAME,
        key,
        ExtraArgs={
            "ACL": "public-read",
            "ContentType": file.content_type,
        },
    )

    return f"https://{BUCKET_NAME}.{REGION}.digitaloceanspaces.com/{key}"