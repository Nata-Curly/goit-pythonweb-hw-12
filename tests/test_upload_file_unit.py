import pytest
from unittest.mock import patch, MagicMock
from src.services.upload_file import UploadFileService


@pytest.fixture
def upload_service():
    return UploadFileService("dummy_cloud", "dummy_key", "dummy_secret")


@patch("src.services.upload_file.cloudinary.uploader.upload")
@patch("src.services.upload_file.cloudinary.CloudinaryImage")
def test_upload_file_success(mock_cloudinary_image, mock_upload, upload_service):
    # Arrange
    mock_file = MagicMock()
    mock_file.file = b"dummy_file"

    mock_upload.return_value = {"version": "123456"}
    mock_image = MagicMock()
    mock_image.build_url.return_value = "http://example.com/image.jpg"
    mock_cloudinary_image.return_value = mock_image

    # Act
    result = upload_service.upload_file(mock_file, "natalia")

    # Assert
    assert result == "http://example.com/image.jpg"
    mock_upload.assert_called_once_with(
        b"dummy_file", public_id="RestApp/natalia", overwrite=True
    )
    mock_image.build_url.assert_called_once_with(
        width=250, height=250, crop="fill", version="123456"
    )
