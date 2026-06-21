

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional
from ..db.dependency import get_db
from ..auth.dependencies import get_current_user
from ..db_models.requests import Request
from ..db_models.ai_request import AIRequest
from ..db_models.user import user as UserModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai-analytics",
    tags=["ai-analytics"]
)


@router.get("/summary")
def get_ai_summary(
    token: str = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):

    try:
        user_id = token.id

        # Calculate date range
        since = datetime.utcnow() - timedelta(days=days)

        # Get AI requests
        ai_requests = (
            db.query(
                func.count(AIRequest.id),
                func.sum(AIRequest.input_tokens),
                func.sum(AIRequest.output_tokens),
                func.sum(AIRequest.total_tokens),
                func.sum(AIRequest.estimated_cost)

            )
            .join(Request, AIRequest.request_id == Request.id)
            .filter(
                Request.user_id == user_id,
                AIRequest.created_at >= since
            )
        )

        if not ai_requests:
            return {
                "total_ai_requests": 0,
                "total_tokens_used": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_estimated_cost": 0.0,
                "by_provider": {},
                "by_model": {},
                "days": days,
            }

        total_requests = len(ai_requests)

        total_input_tokens = sum(
            r.input_tokens or 0 for r in ai_requests
        )
        
        total_output_tokens = sum(
            r.output_tokens or 0 for r in ai_requests
        )
        
        total_tokens = sum(
            r.total_tokens or 0 for r in ai_requests
        )
        
        total_cost = sum(
            r.estimated_cost or 0 for r in ai_requests
        )

        # By provider
        by_provider = {}
        for req in ai_requests:
            if req.provider not in by_provider:
                by_provider[req.provider] = {
                    "requests": 0,
                    "tokens": 0,
                    "cost": 0.0,
                }
            by_provider[req.provider]["requests"] += 1
            by_provider[req.provider]["tokens"] += req.total_tokens or 0
            by_provider[req.provider]["cost"] += req.estimated_cost or 0

        # By model
        by_model = {}
        for req in ai_requests:
            key = f"{req.provider}/{req.model}"
            if key not in by_model:
                by_model[key] = {
                    "requests": 0,
                    "tokens": 0,
                    "cost": 0.0,
                }
            by_model[key]["requests"] += 1
            by_model[key]["tokens"] += req.total_tokens or 0
            by_model[key]["cost"] += req.estimated_cost or 0

        return {
            "total_ai_requests": total_requests,
            "total_tokens_used": total_tokens,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_estimated_cost": round(total_cost, 4),
            "by_provider": by_provider,
            "by_model": by_model,
            "days": days,
        }

    except Exception as e:
        logger.error(f"Error getting AI summary: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve AI summary"
        )


@router.get("/provider-breakdown")
def get_provider_breakdown(
    token: str = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):

    try:
        user_id = token.id
        since = datetime.utcnow() - timedelta(days=days)

        # Query aggregated provider stats
        stats = (
            db.query(
                AIRequest.provider,
                func.count(AIRequest.id).label("request_count"),
                func.sum(AIRequest.total_tokens).label("total_tokens"),
                func.sum(AIRequest.input_tokens).label("input_tokens"),
                func.sum(AIRequest.output_tokens).label("output_tokens"),
                func.sum(AIRequest.estimated_cost).label("total_cost"),
                func.avg(AIRequest.latency_ms).label("avg_latency"),
            )
            .join(Request, AIRequest.request_id == Request.id)
            .filter(
                Request.user_id == user_id,
                AIRequest.created_at >= since
            )
            .group_by(AIRequest.provider)
            .all()
        )

        result = []
        for stat in stats:
            result.append({
                "provider": stat.provider,
                "requests": stat.request_count or 0,
                "tokens": {
                    "input": stat.input_tokens or 0,
                    "output": stat.output_tokens or 0,
                    "total": stat.total_tokens or 0,
                },
                "cost": round(stat.total_cost or 0, 4),
                "avg_latency_ms": round(stat.avg_latency or 0, 2),
            })

        return {
            "providers": result,
            "days": days,
        }

    except Exception as e:
        logger.error(f"Error getting provider breakdown: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve provider breakdown"
        )


@router.get("/models")
def get_model_breakdown(
    token: str = Depends(get_current_user),
    provider: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get usage breakdown by model.

    Optional: Filter by provider (e.g., 'openai', 'anthropic').
    """
    try:
        user_id = token.id
        since = datetime.utcnow() - timedelta(days=days)

        query = (
            db.query(
                AIRequest.provider,
                AIRequest.model,
                func.count(AIRequest.id).label("request_count"),
                func.sum(AIRequest.total_tokens).label("total_tokens"),
                func.sum(AIRequest.estimated_cost).label("total_cost"),
                func.avg(AIRequest.latency_ms).label("avg_latency"),
            )
            .join(Request, AIRequest.request_id == Request.id)
            .filter(
                Request.user_id == user_id,
                AIRequest.created_at >= since
            )
        )

        if provider:
            query = query.filter(
                AIRequest.provider == provider.lower()
            )

        stats = query.group_by(
            AIRequest.provider,
            AIRequest.model
        ).all()

        result = []
        for stat in stats:
            result.append({
                "provider": stat.provider,
                "model": stat.model,
                "requests": stat.request_count or 0,
                "tokens": stat.total_tokens or 0,
                "cost": round(stat.total_cost or 0, 4),
                "avg_latency_ms": round(stat.avg_latency or 0, 2),
            })

        return {
            "models": result,
            "filter": {"provider": provider},
            "days": days,
        }

    except Exception as e:
        logger.error(f"Error getting model breakdown: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve model breakdown"
        )


@router.get("/cost-over-time")
def get_cost_over_time(
    token: str = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):

    try:
        user_id = token.id
        since = datetime.utcnow() - timedelta(days=days)

        stats = (
            db.query(
                func.date(AIRequest.created_at).label("date"),
                AIRequest.provider,
                func.count(AIRequest.id).label("requests"),
                func.sum(AIRequest.estimated_cost).label("daily_cost"),
            )
            .join(Request, AIRequest.request_id == Request.id)
            .filter(
                Request.user_id == user_id,
                AIRequest.created_at >= since
            )
            .group_by(
                func.date(AIRequest.created_at),
                AIRequest.provider
            )
            .order_by(func.date(AIRequest.created_at))
            .all()
        )

        # Aggregate by date
        by_date = {}
        for stat in stats:
            date_str = str(stat.date)
            if date_str not in by_date:
                by_date[date_str] = {
                    "total_cost": 0.0,
                    "requests": 0,
                    "by_provider": {},
                }
            by_date[date_str]["total_cost"] += stat.daily_cost or 0
            by_date[date_str]["requests"] += stat.requests or 0
            by_date[date_str]["by_provider"][stat.provider] = {
                "cost": stat.daily_cost or 0,
                "requests": stat.requests or 0,
            }

        result = [
            {
                "date": date_str,
                "total_cost": round(data["total_cost"], 4),
                "requests": data["requests"],
                "by_provider": {
                    k: {
                        "cost": round(v["cost"], 4),
                        "requests": v["requests"],
                    }
                    for k, v in data["by_provider"].items()
                },
            }
            for date_str, data in sorted(by_date.items())
        ]

        return {
            "daily_costs": result,
            "days": days,
        }

    except Exception as e:
        logger.error(f"Error getting cost over time: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve cost data"
        )


@router.get("/requests")
def get_ai_requests(
    token: str = Depends(get_current_user),
    provider: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):

    try:
        user_id = token.id

        query = (
            db.query(AIRequest, Request)
            .join(Request, AIRequest.request_id == Request.id)
            .filter(Request.user_id == user_id)
        )

        if provider:
            query = query.filter(
                AIRequest.provider == provider.lower()
            )

        if model:
            query = query.filter(
                AIRequest.model.ilike(f"%{model}%")
            )

        # Get total count
        total = query.count()

        # Get paginated results
        results = (
            query.order_by(AIRequest.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        requests = []
        for ai_req, http_req in results:
            requests.append({
                "id": ai_req.id,
                "request_id": ai_req.request_id,
                "provider": ai_req.provider,
                "model": ai_req.model,
                "tokens": {
                    "input": ai_req.input_tokens,
                    "output": ai_req.output_tokens,
                    "total": ai_req.total_tokens,
                },
                "cost": round(ai_req.estimated_cost or 0, 6),
                "latency_ms": ai_req.latency_ms,
                "endpoint": http_req.endpoint,
                "status_code": http_req.status_code,
                "method": http_req.method,
                "tags": ai_req.tags,
                "created_at": ai_req.created_at.isoformat(),
            })

        return {
            "requests": requests,
            "total": total,
            "limit": limit,
            "offset": offset,
            "page": offset // limit + 1 if limit > 0 else 1,
        }

    except Exception as e:
        logger.error(f"Error getting AI requests: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve AI requests"
        )
