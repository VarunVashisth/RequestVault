"""
Updated Capture Router with AI Observability
File: app/routers/capture.py (UPDATED)

Maintains backward compatibility while adding AI detection to the capture flow.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..db.dependency import get_db
from ..SchemaModels.capture_model import capture_model, capture_response
from ..services.request_service import capture_service, sanitize_body
from ..services.ai_services import AIObservabilityService
from ..services import rate_limit_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/capture", response_model=capture_response)
def capture_request(
    request_data: capture_model,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Capture HTTP request with optional AI observability.

    This endpoint now detects and records AI API calls (OpenAI, Claude)
    while maintaining backward compatibility with existing clients.
    """

    # Authenticate API key
    user = capture_service.check(
        request_data.api_key,
        db
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="api_key mismatch"
        )

    # Check rate limits
    if not rate_limit_service.check_rate_limit(
        request_data.api_key
    ):
        raise HTTPException(
            status_code=429,
            detail="Rate Limit Exceeded"
        )

    # Extract client IP
    forwarded_for = request.headers.get(
        "x-forwarded-for"
    )

    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()
    else:
        ip = (
            request.client.host
            if request.client
            else "Unknown"
        )

    # Sanitize request/response data
    request_body = sanitize_body(
        request_data.request_body
    )

    response_body = sanitize_body(
        request_data.response_body
    )

    request_headers = (
        capture_service.sanitize_headers(
            request_data.request_headers
        )
    )

    response_headers = (
        capture_service.sanitize_headers(
            request_data.response_headers
        )
    )

    # Limit sizes
    request_body = capture_service.limit_size(
        request_body
    )

    response_body = capture_service.limit_size(
        response_body
    )

    request_headers = capture_service.limit_size(
        request_headers
    )

    response_headers = capture_service.limit_size(
        response_headers
    )

    # NEW: Detect and process AI requests
    ai_data = None
    if AIObservabilityService.is_ai_request(request_data.endpoint):
        try:
            ai_data = AIObservabilityService.process_ai_request(
                endpoint=request_data.endpoint,
                request_headers=request_headers,
                request_body=request_body,
                response_body=response_body,
                response_time_ms=request_data.response_time_ms,
            )

            if ai_data:
                logger.info(
                    f"AI request detected: {ai_data.get('provider')} "
                    f"{ai_data.get('model')} - Cost: ${ai_data.get('estimated_cost', 'N/A')}"
                )
        except Exception as e:
            logger.error(f"Error processing AI request: {e}")
            # Don't fail the entire capture if AI processing fails

    # Capture request (with AI data if detected)
    result = capture_service.capture(
        user.id,
        request_data.endpoint,
        request_data.status_code,
        request_data.response_time_ms,
        ip,
        request_data.useragent,
        request_data.method,
        request_body,
        response_body,
        request_headers,
        response_headers,
        db,
        ai_data=ai_data,  # NEW: Pass AI data
    )

    # Handle return value (Request or tuple of (Request, AIRequest))
    if isinstance(result, tuple):
        request_obj, ai_request_obj = result
    else:
        request_obj = result

    return request_obj
