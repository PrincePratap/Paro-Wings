from pydantic import BaseModel


class UploadResponseData(BaseModel):
    image_url: str
    file_name: str


class UploadResponse(BaseModel):
    success: bool
    message: str
    data: UploadResponseData
