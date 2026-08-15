from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Status of the application")
    app_name: str = Field(..., description="Name of the service")
    environment: str = Field(..., description="Running environment")
