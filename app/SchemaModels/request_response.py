from pydantic import BaseModel , ConfigDict
from datetime import datetime


class RequestResponse(BaseModel):

    endpoint: str
    status_code: int
    response_time: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)