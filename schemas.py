from pydantic import BaseModel


class EnhanceFolderRequestData(BaseModel):
    studio_name: str
    action_name: str
    month: str
    day: str
    hour: str
