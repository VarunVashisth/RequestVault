from pydantic import BaseModel , ConfigDict
from datetime import datetime


class RequestResponse(BaseModel):

    method: str
    endpoint: str
    status_code: int
    ip_address: str
    useragent: str
    response_time: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)