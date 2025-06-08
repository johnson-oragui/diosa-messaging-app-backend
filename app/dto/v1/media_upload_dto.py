"""
Media upload DTO
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field


# +++++++++++++++++++++++++++++++++++++++  message mdeia upload +++++++++++++++++++++++++++++++++++++++++
# media upload schema
class UploadMessageMediaResponseDto(BaseModel):
    """
    Media upload schema
    """

    message: str = Field(
        default="media uploaded successfully",
        examples=["media uploaded successfully"],
    )
    status_code: int = Field(default=201, examples=[201])
    data: Dict[str, Optional[str]] = Field(
        examples=[{"media_url": "https://media_url.com/image", "media_type": "image"}]
    )
