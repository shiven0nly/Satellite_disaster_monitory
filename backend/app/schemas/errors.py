from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., example="INVALID_FILE_TYPE")
    message: str = Field(..., example="Only .jpg, .jpeg, .png, .tiff, .tif image formats are supported.")


class ErrorResponse(BaseModel):
    error: ErrorDetail
