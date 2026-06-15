from pydantic import BaseModel , ConfigDict



class analytics_response(BaseModel):
        total_requests: int
        avg_response_time:int
        success_requests:int
        failed_requests: int

        model_config = ConfigDict(from_attributes=True)

class TopEndpointResponse(BaseModel):
    endpoint: str
    count: int
    model_config = ConfigDict(from_attributes=True)
