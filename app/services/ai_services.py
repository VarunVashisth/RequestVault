

import re
import json
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)

# Pricing configuration (per 1K tokens)
PROVIDER_PRICING = {
    "openai": {
        "gpt-4-turbo": {
            "input": 0.01,  # $0.01 per 1K input tokens
            "output": 0.03,  # $0.03 per 1K output tokens
        },
        "gpt-4o": {
            "input": 0.005,
            "output": 0.015,
        },
        "gpt-4o-mini": {
            "input": 0.00015,
            "output": 0.0006,
        },
        "gpt-3.5-turbo": {
            "input": 0.0005,
            "output": 0.0015,
        },
        "gpt-4": {
            "input": 0.03,
            "output": 0.06,
        },
    },
    "anthropic": {
        "claude-3-opus": {
            "input": 0.015,  # $0.015 per 1K input tokens
            "output": 0.075,  # $0.075 per 1K output tokens
            "cache_input": 0.00375,  # 25% of input cost for cache
        },
        "claude-3-sonnet": {
            "input": 0.003,
            "output": 0.015,
            "cache_input": 0.00075,
        },
        "claude-3-haiku": {
            "input": 0.00025,
            "output": 0.00125,
            "cache_input": 0.0000625,
        },
        "claude-3-5-sonnet": {
            "input": 0.003,
            "output": 0.015,
            "cache_input": 0.00075,
        },
        "claude-3-5-haiku": {
            "input": 0.00025,
            "output": 0.00125,
            "cache_input": 0.0000625,
        },
    },
}


class AIDetector:
    """Detects AI provider requests from HTTP metadata."""

    @staticmethod
    def detect_provider_and_model(
        endpoint: str,
        request_headers: Optional[Dict] = None,
        request_body: Optional[Dict | str] = None,
        response_body: Optional[Dict | str] = None,
    ) -> Optional[Tuple[str, str]]:

        endpoint_lower = endpoint.lower()

        # OpenAI Detection
        if "openai" in endpoint_lower or "api.openai.com" in endpoint_lower:
            model = AIDetector._extract_openai_model(
                endpoint, request_body, response_body
            )
            if model:
                return ("openai", model)

        # Claude/Anthropic Detection
        if "anthropic" in endpoint_lower or "api.anthropic.com" in endpoint_lower:
            model = AIDetector._extract_claude_model(
                endpoint, request_body, response_body
            )
            if model:
                return ("anthropic", model)

        # Header-based detection
        if request_headers:
            headers_lower = {k.lower(): v for k, v in request_headers.items()}

            if "authorization" in headers_lower:
                auth = headers_lower["authorization"]
                if "bearer sk-proj-" in auth.lower() or "bearer sk-" in auth.lower():
                    model = AIDetector._extract_openai_model(
                        endpoint, request_body, response_body
                    )
                    if model:
                        return ("openai", model)

        return None

    @staticmethod
    def _extract_openai_model(
        endpoint: str, request_body: Optional[Any] = None, response_body: Optional[Any] = None
    ) -> Optional[str]:
        try:
            # Parse request body
            if request_body:
                req = (
                    json.loads(request_body)
                    if isinstance(request_body, str)
                    else request_body
                )
                if isinstance(req, dict) and "model" in req:
                    return req["model"]

            # Parse response body
            if response_body:
                resp = (
                    json.loads(response_body)
                    if isinstance(response_body, str)
                    else response_body
                )
                if isinstance(resp, dict) and "model" in resp:
                    return resp["model"]

            # Fallback: Extract from URL
            if "/v1/chat/completions" in endpoint:
                return "gpt-4"  # Default assumption
        except Exception as e:
            logger.debug(f"Error extracting OpenAI model: {e}")

        return None

    @staticmethod
    def _extract_claude_model(
        endpoint: str, request_body: Optional[Any] = None, response_body: Optional[Any] = None
    ) -> Optional[str]:
        """Extract Claude model from request/response."""
        try:
            if request_body:
                req = (
                    json.loads(request_body)
                    if isinstance(request_body, str)
                    else request_body
                )
                if isinstance(req, dict) and "model" in req:
                    return req["model"]

            if response_body:
                resp = (
                    json.loads(response_body)
                    if isinstance(response_body, str)
                    else response_body
                )
                if isinstance(resp, dict) and "model" in resp:
                    return resp["model"]

            if "/messages" in endpoint:
                return "claude-3-sonnet"  # Default assumption
        except Exception as e:
            logger.debug(f"Error extracting Claude model: {e}")

        return None


class TokenExtractor:

    @staticmethod
    def extract_tokens(
        response_body: Optional[Dict | str] = None,
        provider: Optional[str] = None,
    ) -> Tuple[Optional[int], Optional[int], Optional[int]]:

        if not response_body:
            return None, None, None

        try:
            data = (
                json.loads(response_body)
                if isinstance(response_body, str)
                else response_body
            )

            if not isinstance(data, dict):
                return None, None, None

            if "usage" in data:
                usage = data["usage"]
            
                if provider == "openai":
                    input_tokens = usage.get("prompt_tokens")
                    output_tokens = usage.get("completion_tokens")
                    total_tokens = usage.get("total_tokens")
            
                elif provider == "anthropic":
                    input_tokens = usage.get("input_tokens")
                    output_tokens = usage.get("output_tokens")
                    total_tokens = (
                        (input_tokens or 0)
                        + (output_tokens or 0)
                    )
            
                else:
                    return None, None, None
            
                return (
                    input_tokens,
                    output_tokens,
                    total_tokens,
                )

        except Exception as e:
            logger.debug(f"Error extracting tokens: {e}")

        return None, None, None

    @staticmethod
    def extract_usage_metadata(
        response_body: Optional[Dict | str] = None,
        provider: Optional[str] = None,
    ) -> Optional[Dict]:
        """Extract provider-specific metadata from response."""
        if not response_body:
            return None

        try:
            data = (
                json.loads(response_body)
                if isinstance(response_body, str)
                else response_body
            )

            if not isinstance(data, dict):
                return None

            metadata = {}

            # OpenAI specific
            if provider == "openai":
                if "usage" in data:
                    usage = data["usage"]
                    metadata["prompt_tokens"] = usage.get("prompt_tokens")
                    metadata["completion_tokens"] = usage.get("completion_tokens")
                    metadata["total_tokens"] = usage.get("total_tokens")

                if "choices" in data and data["choices"]:
                    choice = data["choices"][0]
                    metadata["finish_reason"] = choice.get("finish_reason")

            # Claude specific
            elif provider == "anthropic":
                if "usage" in data:
                    usage = data["usage"]
                    metadata["input_tokens"] = usage.get("input_tokens")
                    metadata["output_tokens"] = usage.get("output_tokens")
                    metadata["cache_creation_input_tokens"] = usage.get(
                        "cache_creation_input_tokens"
                    )
                    metadata["cache_read_input_tokens"] = usage.get(
                        "cache_read_input_tokens"
                    )

                metadata["stop_reason"] = data.get("stop_reason")
                metadata["content_type"] = (
                    data.get("content", [{}])[0].get("type")
                    if data.get("content")
                    else None
                )

            return metadata if metadata else None

        except Exception as e:
            logger.debug(f"Error extracting usage metadata: {e}")

        return None


class CostCalculator:
    """Calculates estimated costs for AI API calls."""

    @staticmethod
    def calculate_cost(
        provider: str,
        model: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        cache_creation_tokens: Optional[int] = None,
        cache_read_tokens: Optional[int] = None,
    ) -> Optional[float]:
        """
        Calculate estimated cost in USD.

        Args:
            provider: "openai" or "anthropic"
            model: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cache_creation_tokens: Tokens charged at cache creation (25% of input)
            cache_read_tokens: Tokens charged at cache read (10% of input)

        Returns:
            Estimated cost in USD or None
        """
        try:
            if not input_tokens and not output_tokens:
                return None

            provider_lower = provider.lower()

            if provider_lower not in PROVIDER_PRICING:
                return None

            models = PROVIDER_PRICING[provider_lower]

            # Find matching model (handle version variations)
            pricing = None
            for model_name, rates in models.items():
                if model_name.lower() in model.lower():
                    pricing = rates
                    break

            if not pricing:
                logger.debug(f"No pricing found for {provider} {model}")
                return None

            cost = 0.0

            # Calculate input cost
            if input_tokens:
                base_input_tokens = input_tokens
                if cache_read_tokens:
                    # Cache read tokens cost 10% of input cost
                    base_input_tokens = input_tokens - cache_read_tokens
                    cache_read_cost = (
                        cache_read_tokens * pricing.get("input", 0) * 0.1 / 1000
                    )
                    cost += cache_read_cost

                base_cost = base_input_tokens * pricing.get("input", 0) / 1000
                cost += base_cost

            # Handle cache creation
            if cache_creation_tokens:
                cache_creation_cost = (
                    cache_creation_tokens
                    * pricing.get("cache_input", pricing.get("input", 0) * 0.25)
                    / 1000
                )
                cost += cache_creation_cost

            # Calculate output cost
            if output_tokens:
                output_cost = output_tokens * pricing.get("output", 0) / 1000
                cost += output_cost

            return round(cost, 6)

        except Exception as e:
            logger.debug(f"Error calculating cost: {e}")
            return None


class AIObservabilityService:
    """
    Main service for AI observability.
    Orchestrates detection, token extraction, and cost calculation.
    """

    @staticmethod
    def process_ai_request(
        endpoint: str,
        request_headers: Optional[Dict] = None,
        request_body: Optional[Dict | str] = None,
        response_body: Optional[Dict | str] = None,
        response_time_ms: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Process an HTTP request to extract AI observability data.

        Returns:
            Dictionary with AI metadata or None if not an AI request
        """
        try:
            # Step 1: Detect provider and model
            result = AIDetector.detect_provider_and_model(
                endpoint, request_headers, request_body, response_body
            )

            if not result:
                return None

            provider, model = result

            # Step 2: Extract token usage
            input_tokens, output_tokens, total_tokens = TokenExtractor.extract_tokens(
                response_body, provider
            )

            # Step 3: Extract metadata
            usage_metadata = TokenExtractor.extract_usage_metadata(
                response_body, provider
            )

            # Step 4: Calculate cost
            cache_creation_tokens = None
            cache_read_tokens = None

            if usage_metadata:
                cache_creation_tokens = usage_metadata.get(
                    "cache_creation_input_tokens"
                )
                cache_read_tokens = usage_metadata.get("cache_read_input_tokens")

            estimated_cost = CostCalculator.calculate_cost(
                provider=provider,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cache_creation_tokens=cache_creation_tokens,
                cache_read_tokens=cache_read_tokens,
            )

            # Step 5: Build result
            ai_data = {
                "provider": provider,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "estimated_cost": estimated_cost,
                "latency_ms": response_time_ms,
                "usage_metadata": usage_metadata,
                "tags": ["ai", provider],
            }

            logger.info(
                f"AI request detected: {provider} {model} - "
                f"Tokens: {total_tokens} - Cost: ${estimated_cost}"
            )

            return ai_data

        except Exception as e:
            logger.error(f"Error processing AI request: {e}")
            return None

    @staticmethod
    def is_ai_request(endpoint: str) -> bool:
        """Quick check if URL is likely an AI API endpoint."""
        ai_patterns = [
            "openai",
            "anthropic",
            "api.openai.com",
            "api.anthropic.com",
            "/v1/chat/completions",
            "/v1/messages",
            "/messages",
        ]
        endpoint_lower = endpoint.lower()
        return any(pattern in endpoint_lower for pattern in ai_patterns)
