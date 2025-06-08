"""
MediaUploadService module
"""

import typing
from asyncio import to_thread
from uuid import uuid4
import re
import os
from io import BytesIO


from fastapi import HTTPException, UploadFile, Request
import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError
from PIL import Image

from app.utils.task_logger import create_logger
from app.core.config import settings
from app.dto.v1.media_upload_dto import UploadMessageMediaResponseDto


logger = create_logger(":: MediaUploadService Service ::")


class MediaUploadService:
    """
    DirectMessage Service
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.cloudinary_api_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
            secured=True,
        )

        self.image_content_types = {
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/webp",
            "image/svg+xml",
            "image/bmp",
            "image/tiff",
            "image/gif",
        }
        self.video_content_types = {
            "video/mp4",
            "video/webm",
            "video/ogg",
            "video/quicktime",
            "audio/mpeg",
            "audio/ogg",
            "audio/webm",
            "audio/mp4",
            "audio/m4a",
            # "audio/x-ms-wma",
            # "audio/flac",
            # "audio/3gpp",
            # "audio/amr",
        }

        self.file_content_types = {
            "text/csv",
            "application/json",
            "application/xml",
            "application/x-yaml",
            "application/zip",
            "application/gzip",
            "application/x-7z-compressed",
            "application/pdf",
            "application/msword",
            "application/vnd.ms-excel",
            "text/plain",
            "application/vnd.ms-powerpoint",
        }

    async def validate_media_and_upload(
        self, request: Request, media_to_upload: UploadFile, file_type: str
    ) -> typing.Union[UploadMessageMediaResponseDto, None]:
        """
        Validates media file and uploads to cloud
        """
        claims: dict = request.state.claims
        current_user_id = claims.get("user_id")
        if file_type == "image":
            if media_to_upload.content_type not in self.image_content_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported content_type. content_type must be one of {self.image_content_types}",
                )
            if media_to_upload.size and media_to_upload.size > 4 * 1024 * 1024:  # 4MB
                raise HTTPException(
                    status_code=400, detail="FIle size exceeds the limit of 4MB"
                )
            if not media_to_upload.size:
                raise HTTPException(
                    status_code=400, detail="Image is without size. Invalid image file"
                )

            photo_name = f"{uuid4()}_{current_user_id}"
            if media_to_upload.filename:
                photo_name, _ = os.path.splitext(media_to_upload.filename)
                photo_name = re.sub(r"[^\w\-_\.]", "_", photo_name)
                photo_name = f"{photo_name}_{current_user_id}"

            media_url = await self.upload_to_cloudinary(
                file=media_to_upload,
                folder="message-images",
                file_name=photo_name,
                file_type=file_type,
                resource_type="image",
            )

            return UploadMessageMediaResponseDto(
                data={"media_url": media_url, "media_type": file_type}
            )
        if file_type == "video" or file_type == "audio":
            if media_to_upload.content_type not in self.video_content_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported content_type. content_type must be one of {self.video_content_types}",
                )
            if media_to_upload.size and media_to_upload.size > 5 * 1024 * 1024:  # 5MB
                raise HTTPException(
                    status_code=400, detail="FIle size exceeds the limit of 5MB"
                )
            if not media_to_upload.size:
                raise HTTPException(
                    status_code=400,
                    detail=f"{file_type} is without size. Invalid {file_type} file",
                )

            video_name = f"{uuid4()}_{current_user_id}"
            if media_to_upload.filename:
                video_name, _ = os.path.splitext(media_to_upload.filename)
                video_name = re.sub(r"[^\w\-_\.]", "_", video_name)
                video_name = f"{video_name}_{current_user_id}"

            media_url = await self.upload_to_cloudinary(
                file=media_to_upload,
                folder=f"message-{file_type}s",
                file_name=video_name,
                file_type=file_type,
                resource_type="video",
            )

            return UploadMessageMediaResponseDto(
                data={"media_url": media_url, "media_type": file_type}
            )

        if not media_to_upload.content_type:
            raise HTTPException(status_code=400, detail="Content type missing")
        if media_to_upload.content_type not in self.file_content_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported content_type. content_type must be one of {self.file_content_types}",
            )
        if media_to_upload.size and media_to_upload.size > 1 * 1024 * 1024:  # 1MB
            raise HTTPException(
                status_code=400, detail="FIle size exceeds the limit of 1MB"
            )
        if not media_to_upload.size:
            raise HTTPException(
                status_code=400,
                detail=f"{file_type} is without size. Invalid {file_type} file",
            )

        file_name = f"{uuid4()}_{current_user_id}"
        if media_to_upload.filename:
            file_name, _ = os.path.splitext(media_to_upload.filename)
            file_name = re.sub(r"[^\w\-_\.]", "_", file_name)
            file_name = f"{file_name}_{current_user_id}"

        media_url = await self.upload_to_cloudinary(
            file=media_to_upload,
            folder=f"message-{file_type}s",
            file_name=file_name,
            file_type=file_type,
            resource_type="raw",
        )

        return UploadMessageMediaResponseDto(
            data={"media_url": media_url, "media_type": file_type}
        )

    async def upload_to_cloudinary(
        self,
        file: UploadFile,
        folder: str,
        file_name: str,
        file_type: str,
        resource_type: str,
    ) -> typing.Union[str, None]:
        """
        Uploads a file to Cloudinary and returns the direct download URL.

        Args:
            file (UploadFile): File to upload
            folder (str): Cloudinary folder to store the file in. videos or images.
            resource_type (str): The name of the resource. e.g (video, audio, image)
                Note: Use the video resource type for all video assets as well as for audio files, such as .mp3.

        Returns:
            str: Direct download URL of the uploaded file
        """
        product_id_prefix = f"{file_type}s"

        try:
            result = await to_thread(
                cloudinary.uploader.upload,
                file=file.file,
                asset_folder=folder,
                resource_type=resource_type,
                public_id=file_name,
                product_id_prefix=product_id_prefix,
                use_filename=True,
                use_filename_as_display_name=True,
                unique_filename=False,
                overwrite=False,
                eager=(
                    []
                    if file_type != "video"
                    else [
                        {
                            "width": 720,  # Set a target width (or height if using scale)
                            "crop": "scale",  # Scale to fit width, maintaining aspect ratio
                            "quality": "auto",  # Apply the desired quality preset
                            "format": "mp4",  # Ensure output is mp4 for broad compatibility
                            "fetch_format": "auto",  # Auto-select format for delivery
                        }
                    ]
                ),
                eager_async=True,
            )
            # Get the file URL and append `fl_attachment` for direct download
            return result.get("secure_url")
        except CloudinaryError as exc:
            logger.error("Error uploading file to cloudinary: %s", str(exc))
            raise HTTPException(status_code=417, detail="File upload failed") from exc

    async def compress_image(
        self, upload_file: UploadFile, quality: int = 70
    ) -> BytesIO:
        """
        Compresses images
        """
        image = Image.open(await upload_file.read())
        buffer = BytesIO()

        if image.mode != "RGB":
            image = image.convert("RGB")

        image.save(buffer, format="JPEG", optimize=True, quality=quality)
        buffer.seek(0)
        return buffer


media_upload_service = MediaUploadService()
