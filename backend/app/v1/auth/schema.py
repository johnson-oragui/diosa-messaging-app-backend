from pydantic import BaseModel, Field

class AccessToken(BaseModel):
    access_token: str = Field(examples=['12wxc3.55v44f3A.4f5gh5n67yn...'])
