from pydantic import BaseModel , ConfigDict
from datetime import datetime


class RequestResponse(BaseModel):

    method: str
    endpoint: str
    status_code: int
    ip_address: str
    useragent: str
    response_time: int
    request_body: dict | None
    response_body: dict | None
    request_headers: dict | None
    response_headers: dict | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)