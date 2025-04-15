import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    Service class for uploading files to Cloudinary."""
    def __init__(self, cloud_name, api_key, api_secret):
        """
        Initialize the UploadFileService with the given Cloudinary
        configuration values.

        :param cloud_name: The name of the Cloudinary cloud.
        :param api_key: The Cloudinary API key.
        :param api_secret: The Cloudinary API secret.
        :return: None
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Uploads a file to Cloudinary and returns the URL of the uploaded image.

        Args:
            file: The file to upload.
            username: The username of the user to associate with the image.

        Returns:
            The URL of the uploaded image.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
