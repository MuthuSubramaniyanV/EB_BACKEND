import os
import boto3
from sqlmodel import Session
from app.core.database import engine
from app.modules.uploads.model import MeterUpload
from dotenv import load_dotenv

load_dotenv()


class FilebaseRepository:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=os.getenv("FILEBASE_ENDPOINT"),
            aws_access_key_id=os.getenv("FILEBASE_KEY"),
            aws_secret_access_key=os.getenv("FILEBASE_SECRET"),
            region_name="us-east-1",
        )
        self.bucket = os.getenv("FILEBASE_BUCKET")

    def upload_file(self, content: bytes, file_name: str, content_type: str):
        self.s3.put_object(
            Bucket=self.bucket,
            Key=file_name,
            Body=content,
            ContentType=content_type,
        )

        endpoint = os.getenv("FILEBASE_ENDPOINT")
        return f"{endpoint}/{self.bucket}/{file_name}"

    def save_metadata_to_db(
        self,
        file_name: str,
        image_url: str,
        timestamp,
        status: str,
    ) -> MeterUpload:

        if not engine:
            raise RuntimeError("Database engine is not initialized")

        with Session(engine) as session:
            upload = MeterUpload(
                file_name=file_name,
                image_url=image_url,
                timestamp=timestamp,
                status=status,
            )
            session.add(upload)
            session.commit()
            session.refresh(upload)
            return upload
