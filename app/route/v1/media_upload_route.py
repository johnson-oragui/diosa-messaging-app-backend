"""
Media upload Route Module
"""

import typing
from fastapi import APIRouter, status, Request, Depends, UploadFile

from app.utils.responses import responses
from app.service.v1.media_upload_service import media_upload_service
from app.dto.v1.media_upload_dto import UploadMessageMediaResponseDto
from app.core.security import validate_logout_status


media_upload_router = APIRouter(prefix="/media-uploads", tags=["MEDIA UPLOAD"])


@media_upload_router.post(
    "/images",
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    response_model=UploadMessageMediaResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def upload_images(
    request: Request, media_to_upload: UploadFile
) -> typing.Optional[UploadMessageMediaResponseDto]:
    """
    Uploads images.

    Return:
        Success message upon success
    Raises:
        422
        500
        409
        401
        404
    """
    return await media_upload_service.validate_media_and_upload(
        media_to_upload=media_to_upload, request=request, file_type="image"
    )


@media_upload_router.post(
    "/videos",
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    response_model=UploadMessageMediaResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def upload_videos(
    request: Request, media_to_upload: UploadFile
) -> typing.Optional[UploadMessageMediaResponseDto]:
    """
    Uploads images.

    Return:
        Success message upon success
    Raises:
        422
        500
        409
        401
        404
    """
    return await media_upload_service.validate_media_and_upload(
        media_to_upload=media_to_upload, request=request, file_type="video"
    )


@media_upload_router.post(
    "/audios",
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    response_model=UploadMessageMediaResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def upload_audios(
    request: Request, media_to_upload: UploadFile
) -> typing.Optional[UploadMessageMediaResponseDto]:
    """
    Uploads audios.

    Return:
        Success message upon success
    Raises:
        422
        500
        409
        401
        404
    """
    return await media_upload_service.validate_media_and_upload(
        media_to_upload=media_to_upload, request=request, file_type="audio"
    )


@media_upload_router.post(
    "/files",
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    response_model=UploadMessageMediaResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def upload_files(
    request: Request, media_to_upload: UploadFile
) -> typing.Optional[UploadMessageMediaResponseDto]:
    """
    Uploads files.

    Return:
        Success message upon success
    Raises:
        422
        500
        409
        401
        404
    """
    return await media_upload_service.validate_media_and_upload(
        media_to_upload=media_to_upload, request=request, file_type="file"
    )
