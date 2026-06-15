from pydantic import BaseModel , ConfigDict
from datetime import datetime
from typing import Any


class RequestResponse(BaseModel):

    method: str
    endpoint: str
    status_code: int
    ip_address: str
    useragent: str | None
    response_time: int
    request_body: Any = None
    response_body: Any = None
    request_headers: dict | None
    response_headers: dict | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AnalyticResponse(BaseModel):

    method: str
    endpoint: str
    status_code: int
    ip_address: str
    response_time: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)