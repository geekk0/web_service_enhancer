from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder


class EnhanceFolderRequestData(BaseModel):
    studio_name: str
    action_name: str
    month: str
    day: str
    hour: str
    task: bool
    cert_code: str | None = None


class ProcessFolderResult(BaseModel):
    status: str
    message: str | None = None
    execution_time: float | None = None
    error: bool = False
    error_type: str | None = None
    error_message: str | None = None
    folder_name: str | None = None

    def json(self, **kwargs):
        return jsonable_encoder(self)
