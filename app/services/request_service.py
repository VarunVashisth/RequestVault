"""
Updated Request Service with AI Observability Integration
File: app/services/request_service.py (UPDATED)

Extends the existing request_service.py with AI detection and storage.
Maintains backward compatibility with existing code.
"""

from ..db_models.user import user
from ..db_models.requests import Request
from ..db_models.ai_request import AIRequest
from .ai_services import AIObservabilityService
import json
from decimal import Decimal
from datetime import date, datetime
import logging

logger = logging.getLogger(__name__)

MAX_BODY_SIZE = 10000

SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "set-cookie",
    "token",
    "secret",
    "api-key",
    "apikey",
    "auth",
    "jwt",
}

SENSITIVE_FIELDS = {
    "password",
    "token",
    "secret",
    "auth",
    "credential",
    "jwt",
    "cookie",
    "api_key",
    "private_key",
    "secret_key",
}


def sanitize_body(data):
    """Existing sanitization logic - unchanged."""

    if data is None:
        return None

    if isinstance(data, (bytes, bytearray)):

        try:
            decoded = data.decode("utf-8")

            try:
                return sanitize_body(
                    json.loads(decoded)
                )

            except Exception:
                return decoded

        except Exception:
            return "[BINARY_DATA]"

    if isinstance(data, (datetime, date)):
        return data.isoformat()

    if isinstance(data, Decimal):
        return float(data)

    if isinstance(data, dict):

        cleaned = {}

        for key, value in data.items():

            key_str = str(key)
            lower_key = key_str.lower()

            if any(
                pattern in lower_key
                for pattern in SENSITIVE_FIELDS
            ):
                cleaned[key_str] = "[REDACTED]"

            else:
                cleaned[key_str] = sanitize_body(value)

        return cleaned

    if isinstance(data, list):
        return [sanitize_body(item) for item in data]

    if isinstance(data, tuple):
        return [sanitize_body(item) for item in data]

    if isinstance(data, set):
        return [sanitize_body(item) for item in data]

    if isinstance(data, str):

        stripped = data.strip()

        if (
            stripped.startswith("{")
            or stripped.startswith("[")
        ):
            try:
                parsed = json.loads(data)

                return sanitize_body(parsed)

            except Exception:
                pass

        return data

    if isinstance(data, (bool, int, float)):
        return data

    try:
        return str(data)

    except Exception:
        return "[UNSERIALIZABLE_OBJECT]"


class capture_service():

    @staticmethod
    def check(api: str, db):
        """Existing check logic - unchanged."""

        check_user = (
            db.query(user).filter(user.api_key == api).first()
        )

        return check_user

    @staticmethod
    def capture(
        id: int,
        endpoint: str,
        status_code: int,
        response_time: int,
        ip: str,
        user_agent: str,
        method: str,
        request_body,
        response_body,
        request_headers,
        response_headers,
        db,
        # New optional parameters for AI observability
        ai_data: dict = None,
    ):
        """
        Capture HTTP request with optional AI observability data.

        Args:
            id: User ID
            endpoint: Request endpoint
            status_code: HTTP status code
            response_time: Response time in milliseconds
            ip: Client IP address
            user_agent: User agent string
            method: HTTP method
            request_body: Request body
            response_body: Response body
            request_headers: Request headers
            response_headers: Response headers
            db: Database session
            ai_data: Optional AI observability data dictionary

        Returns:
            The captured Request object, or tuple of (Request, AIRequest) if AI data present
        """

        try:
            # Create main request record
            capture = Request(
                user_id=id,
                ip_address=ip,
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                useragent=user_agent,
                response_time=response_time,
                request_body=request_body,
                response_body=response_body,
                request_headers=request_headers,
                response_headers=response_headers,
            )

            db.add(capture)
            db.flush()  # Flush to get the ID without committing

            # If AI data present, create AIRequest record
            ai_request = None
            if ai_data:
                try:
                    ai_request = AIRequest(
                        request_id=capture.id,
                        provider=ai_data.get("provider"),
                        model=ai_data.get("model"),
                        input_tokens=ai_data.get("input_tokens"),
                        output_tokens=ai_data.get("output_tokens"),
                        total_tokens=ai_data.get("total_tokens"),
                        estimated_cost=ai_data.get("estimated_cost"),
                        latency_ms=ai_data.get("latency_ms"),
                        usage_metadata=ai_data.get("usage_metadata"),
                        tags=ai_data.get("tags"),
                    )

                    db.add(ai_request)
                    logger.info(
                        f"AI request recorded: {ai_data.get('provider')} "
                        f"{ai_data.get('model')} - ID: {capture.id}"
                    )

                except Exception as e:
                    logger.error(f"Failed to create AI request record: {e}")
                    # Don't fail the entire capture if AI record fails
                    pass

            db.commit()
            db.refresh(capture)

            return (capture, ai_request) if ai_request else capture

        except Exception as e:
            logger.error(f"Error in capture: {e}")
            db.rollback()
            raise

    @staticmethod
    def process_and_capture(
        id: int,
        endpoint: str,
        status_code: int,
        response_time: int,
        ip: str,
        user_agent: str,
        method: str,
        request_body,
        response_body,
        request_headers,
        response_headers,
        db,
    ):
        """
        Full request processing pipeline with AI detection.
        This is the recommended entry point for new code.

        Args:
            All capture() parameters without ai_data

        Returns:
            Tuple of (Request, AIRequest | None)
        """

        # Sanitize data
        request_body = sanitize_body(request_body)
        response_body = sanitize_body(response_body)
        request_headers = capture_service.sanitize_headers(request_headers)
        response_headers = capture_service.sanitize_headers(response_headers)

        # Limit sizes
        request_body = capture_service.limit_size(request_body)
        response_body = capture_service.limit_size(response_body)
        request_headers = capture_service.limit_size(request_headers)
        response_headers = capture_service.limit_size(response_headers)

        # Detect and process AI requests
        ai_data = None
        if AIObservabilityService.is_ai_request(endpoint):
            ai_data = AIObservabilityService.process_ai_request(
                endpoint=endpoint,
                request_headers=request_headers,
                request_body=request_body,
                response_body=response_body,
                response_time_ms=response_time,
            )

        # Capture request with AI data if present
        result = capture_service.capture(
            user_id=id,
            endpoint=endpoint,
            status_code=status_code,
            response_time=response_time,
            ip=ip,
            user_agent=user_agent,
            method=method,
            request_body=request_body,
            response_body=response_body,
            request_headers=request_headers,
            response_headers=response_headers,
            db=db,
            ai_data=ai_data,
        )

        return result

    @staticmethod
    def sanitize_headers(headers):
        """Existing header sanitization logic - unchanged."""

        if not headers:
            return None

        cleaned = {}

        for key, value in headers.items():

            key_str = str(key)
            lower_key = key_str.lower()

            if any(
                pattern in lower_key
                for pattern in SENSITIVE_HEADERS
            ):
                cleaned[key_str] = "[REDACTED]"
                continue

            if value is None:
                cleaned[key_str] = None

            elif isinstance(
                value,
                (bool, int, float, str)
            ):
                cleaned[key_str] = value

            elif isinstance(
                value,
                (bytes, bytearray)
            ):
                try:
                    decoded = value.decode("utf-8")

                    try:
                        cleaned[key_str] = json.loads(decoded)

                    except Exception:
                        cleaned[key_str] = decoded

                except Exception:
                    cleaned[key_str] = "[BINARY_DATA]"

            else:
                try:
                    cleaned[key_str] = repr(value)
                except Exception:
                    cleaned[key_str] = "[UNSERIALIZABLE_HEADER]"

        return cleaned

    @staticmethod
    def limit_size(data):
        """Existing size limiting logic - unchanged."""
        if data is None:
            return None

        try:
            text = json.dumps(
                data,
                default=str,
                ensure_ascii=False
            )

        except Exception:
            text = str(data)

        if len(text) <= MAX_BODY_SIZE:
            return data

        return {
            "truncated": True,
            "original_size": len(text),
            "preview_size": MAX_BODY_SIZE,
            "preview": text[:MAX_BODY_SIZE]
        }
