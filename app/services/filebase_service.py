import os

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


class FilebaseService:
    def __init__(self):
        self.endpoint = settings.FILEBASE_ENDPOINT or os.getenv("FILEBASE_ENDPOINT")
        self.access_key = settings.FILEBASE_KEY or os.getenv("FILEBASE_KEY")
        self.secret_key = settings.FILEBASE_SECRET or os.getenv("FILEBASE_SECRET")
        self.bucket = settings.FILEBASE_BUCKET or os.getenv("FILEBASE_BUCKET")

        if not all([self.endpoint, self.access_key, self.secret_key, self.bucket]):
            raise RuntimeError("Filebase storage is not configured")

        self.s3 = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name="us-east-1",
        )

    def upload_image(self, content: bytes, file_name: str, content_type: str) -> str:
        self.s3.put_object(
            Bucket=self.bucket,
            Key=file_name,
            Body=content,
            ContentType=content_type,
        )
        return self.get_public_url(file_name)

    def delete_image(self, file_name: str) -> None:
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=file_name)
        except ClientError as exc:
            raise RuntimeError(f"Failed to delete file {file_name}: {exc}") from exc

    def get_public_url(self, file_name: str) -> str:
        if settings.FILEBASE_PUBLIC_BASE_URL:
            return f"{settings.FILEBASE_PUBLIC_BASE_URL.rstrip('/')}/{file_name}"
        return f"{self.endpoint.rstrip('/')}/{self.bucket}/{file_name}"

    def get_image_bytes(self, file_name: str) -> bytes:
        """Download an object from the configured Filebase bucket and return its bytes."""
        try:
            obj = self.s3.get_object(Bucket=self.bucket, Key=file_name)
            return obj["Body"].read()
        except ClientError as exc:
            raise RuntimeError(f"Failed to get file {file_name}: {exc}") from exc
