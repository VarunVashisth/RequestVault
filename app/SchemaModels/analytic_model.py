from pydantic import BaseModel

class analytics_request(BaseModel):
    api_key: str


class analytics_response(BaseModel):
    total_requests: int
    avg_response_time: float
    success_requests: int
    failed_requests: int