"""
Updated Capture Model with AI Support
File: app/SchemaModels/capture_model.py (UPDATED)

Extends the existing model with optional AI observability fields.
Maintains backward compatibility - all new fields are optional.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


# Request body
class capture_model(BaseModel):
    """
    Capture request model - captures HTTP request/response data.
    
    New optional fields for AI observability:
    - ai_provider: Detected AI provider (openai, anthropic, etc.)
    - ai_model: AI model used
    - ai_tokens: Token usage information
    - ai_cost: Estimated cost
    - tags: Request categorization tags
    """

    api_key: str

    method: str
    useragent: Optional[str] = None

    endpoint: str
    status_code: int
    response_time_ms: int

    request_headers: Optional[Dict[str, Any]] = None
    response_headers: Optional[Dict[str, Any]] = None

    request_body: Optional[Dict | str | list] = None
    response_body: Optional[Dict | str | list] = None

    # NEW: AI Observability Fields (optional for backward compatibility)
    ai_provider: Optional[str] = Field(
        None,
        description="AI provider: openai, anthropic, etc."
    )
    ai_model: Optional[str] = Field(
        None,
        description="Model identifier: gpt-4, claude-3-opus, etc."
    )
    ai_tokens: Optional[Dict[str, int]] = Field(
        None,
        description="Token usage: {input, output, total}"
    )
    ai_cost: Optional[float] = Field(
        None,
        description="Estimated cost in USD"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Request tags for categorization"
    )


# Response body
class capture_response(BaseModel):
    """Response model for capture endpoint."""

    method: str
    endpoint: str
    status_code: int
    response_time: int
    ip_address: str
    useragent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# AI Request Query Model
class AIRequestQuery(BaseModel):
    """Model for querying AI requests."""

    provider: Optional[str] = None
    model: Optional[str] = None
    limit: int = Field(50, ge=1, le=500)
    offset: int = Field(0, ge=0)
    sort_by: str = Field("created_at", pattern="^(created_at|cost|tokens)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


# AI Summary Response
class AISummaryResponse(BaseModel):
    """Summary of AI usage."""

    total_ai_requests: int
    total_tokens_used: int
    total_input_tokens: int
    total_output_tokens: int
    total_estimated_cost: float
    by_provider: Dict[str, Dict[str, Any]]
    by_model: Dict[str, Dict[str, Any]]
    days: int


# AI Request Detail Model
class AIRequestDetail(BaseModel):
    """Detailed AI request information."""

    id: int
    request_id: int
    provider: str
    model: str
    tokens: Dict[str, Optional[int]]
    cost: float
    latency_ms: Optional[int]
    endpoint: str
    status_code: int
    method: str
    tags: Optional[List[str]]
    created_at: str

    class Config:
        from_attributes = True
