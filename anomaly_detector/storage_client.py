"""MinIO/S3 compatible storage client wrapper for model ML artifacts and reports.
"""

import json
import os
from typing import Any

import boto3
import joblib


class StorageClient:
    """Wrapper around boto3 for saving/loading objects from MinIO/S3."""

    def __init__(self) -> None:
        """Initialize the boto3 client using environment variables.

        Defaults to local MinIO if AWS environment variables are not present.
        """
        # Read from environment with fallbacks to local docker-compose defaults
        endpoint_url = os.environ.get("S3_ENDPOINT_URL", "http://localhost:9000")
        access_key = os.environ.get("AWS_ACCESS_KEY_ID", "minioadmin")
        secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "minioadmin")

        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="us-east-1", # boto3 requires a region name even for MinIO
        )
        self.model_bucket = "model-artifacts"
        self.report_bucket = "reports"

    def save_model(self, model: Any, object_name: str) -> None:
        """Serialize a scikit-learn model via joblib and upload to objects bucket."""
        # joblib requires a file-like object or a local path.
        # Using a temporary local file, then uploading and deleting it.
        tmp_path = f"/tmp/{object_name}"
        joblib.dump(model, tmp_path)
        try:
            self.client.upload_file(tmp_path, self.model_bucket, object_name)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def load_model(self, object_name: str) -> Any:
        """Download scikit-learn model from artifacts bucket and deserialize it."""
        tmp_path = f"/tmp/{object_name}"
        self.client.download_file(self.model_bucket, object_name, tmp_path)
        try:
            model = joblib.load(tmp_path)
            return model
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def save_report(self, report_dict: dict[str, Any], object_name: str) -> None:
        """Save a dictionary as a JSON file to the reports bucket."""
        json_str = json.dumps(report_dict, indent=2)
        self.client.put_object(
            Bucket=self.report_bucket,
            Key=object_name,
            Body=json_str.encode("utf-8"),
            ContentType="application/json",
        )

    def load_report(self, object_name: str) -> dict[str, Any]:
        """Load a JSON report from the reports bucket."""
        response = self.client.get_object(Bucket=self.report_bucket, Key=object_name)
        json_str = response["Body"].read().decode("utf-8")
        return dict(json.loads(json_str))
