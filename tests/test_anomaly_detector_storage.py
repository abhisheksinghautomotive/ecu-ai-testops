import os
from unittest.mock import MagicMock, patch

from anomaly_detector.storage_client import StorageClient


@patch("anomaly_detector.storage_client.boto3.client")
def test_storage_client_init(mock_boto: MagicMock) -> None:
    mock_s3 = MagicMock()
    mock_boto.return_value = mock_s3

    # Test valid init
    os.environ["S3_ENDPOINT_URL"] = "http://localhost:9000"
    os.environ["AWS_ACCESS_KEY_ID"] = "admin"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "password"

    StorageClient()
    # verify underlying mocked boto is initialized
    mock_boto.assert_called_with(
        "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id="admin",
        aws_secret_access_key="password",
        region_name="us-east-1"
    )


@patch("anomaly_detector.storage_client.boto3.client")
def test_storage_client_save_load_model(mock_boto: MagicMock) -> None:
    mock_s3 = MagicMock()
    mock_boto.return_value = mock_s3

    os.environ["S3_ENDPOINT_URL"] = "http://localhost:9000"
    os.environ["AWS_ACCESS_KEY_ID"] = "admin"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "password"

    client = StorageClient()

    # Test save_model
    dummy_model = {"UDS": "model_1", "OBD": "model_2"}
    client.save_model(dummy_model, "test_model.pkl")
    mock_s3.upload_file.assert_called_once()

    # Test load_model
    # we just need to mock what load_model does under the hood (download_file)
    import joblib
    with open("/tmp/test_download.pkl", "wb") as f:
        joblib.dump(dummy_model, f)

    def side_effect(bucket: str, key: str, path: str) -> None:
        import shutil
        shutil.copy("/tmp/test_download.pkl", path)

    mock_s3.download_file.side_effect = side_effect
    loaded_model = client.load_model("test_model.pkl")
    assert loaded_model == dummy_model


@patch("anomaly_detector.storage_client.boto3.client")
def test_storage_client_save_report(mock_boto: MagicMock) -> None:
    mock_s3 = MagicMock()
    mock_boto.return_value = mock_s3

    os.environ["MINIO_ENDPOINT"] = "http://localhost:9000"
    os.environ["MINIO_ACCESS_KEY"] = "admin"
    os.environ["MINIO_SECRET_KEY"] = "password"

    client = StorageClient()

    # Test save_report
    dummy_report = {"test": "data"}
    client.save_report(dummy_report, "test_report.json")
    mock_s3.put_object.assert_called_once()

    # Verify it put JSON
    call_args = mock_s3.put_object.call_args[1]
    assert call_args["Bucket"] == client.report_bucket
    assert call_args["Key"] == "test_report.json"
    assert b'"test": "data"' in call_args["Body"]
