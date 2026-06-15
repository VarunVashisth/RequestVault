from fastapi import HTTPException
from sqlalchemy import func , or_
from typing import Annotated
from ..db_models.user import user
from ..db_models.requests import Request


class analytics_service:

    @staticmethod
    def analytics(user_id: int, db):

        existing_user = (
            db.query(user)
            .filter(user.id == user_id)
            .first()
        )

        if not existing_user:
            return {
                "total_requests": 0,
                "avg_response_time": 0,
                "success_requests": 0,
                "failed_requests": 0
            }

        total_requests = (
            db.query(Request)
            .filter(
                Request.user_id == existing_user.id
            )
            .count()
        )

        avg_response_time = (
            db.query(
                func.avg(Request.response_time)
            )
            .filter(
                Request.user_id == existing_user.id
            )
            .scalar()
        ) or 0

        success_requests = (
            db.query(Request)
            .filter(
                Request.user_id == existing_user.id,
                Request.status_code < 400
            )
            .count()
        )

        failed_requests = (
            db.query(Request)
            .filter(
                Request.user_id == existing_user.id
                ).filter(
                    or_(
                        Request.status_code == 0,
                        Request.status_code >= 400
                    )
                )
                .count()
            )
            
        

        return {
            "total_requests": total_requests,
            "avg_response_time": int(avg_response_time),
            "success_requests": success_requests,
            "failed_requests": failed_requests
        }
    
    @staticmethod
    def get_requests(
        user_id: int,
        search: str | None,
        status_code: int | None,
        method: str | None,
        sort: str,
        cursor: int | None,
        limit: int,
        db
    ):
    
        if limit > 100:
            limit = 100
    
        query = (
            db.query(Request)
            .filter(Request.user_id == user_id)
        )
    
        if search:
            query = query.filter(
                Request.endpoint.ilike(
                    f"%{search}%"
                )
            )
    
        # FIX 1: Status ranges instead of exact match
        if status_code is not None:
    
            if status_code == 200:
                query = query.filter(
                    Request.status_code >= 200,
                    Request.status_code < 300
                )
    
            elif status_code == 300:
                query = query.filter(
                    Request.status_code >= 300,
                    Request.status_code < 400
                )
    
            elif status_code == 400:
                query = query.filter(
                    Request.status_code >= 400,
                    Request.status_code < 500
                )
    
            elif status_code == 500:
                query = query.filter(
                    Request.status_code >= 500
                )
    
            else:
                query = query.filter(
                    Request.status_code == status_code
                )
    
        # FIX 2: Case-insensitive method filtering
        if method:
            query = query.filter(
                func.upper(Request.method)
                == method.upper()
            )
    
        if sort not in ["asc", "desc"]:
            sort = "desc"
    
        if sort == "asc":
    
            if cursor is not None:
                query = query.filter(
                    Request.id > cursor
                )
    
            query = query.order_by(
                Request.id.asc()
            )
    
        else:
    
            if cursor is not None:
                query = query.filter(
                    Request.id < cursor
                )
    
            query = query.order_by(
                Request.id.desc()
            )
    
        return query.limit(limit).all()
    
    @staticmethod
    def get_request_by_id(
        request_id: int,
        user_id: int,
        db
    ):
    
        return (
            db.query(Request)
            .filter(
                Request.id == request_id,
                Request.user_id == user_id
            )
            .first()
        )
    
    @staticmethod
    def delete_request(
        request_id: int,
        user_id: int,
        db
    ):
    
        request = (
            db.query(Request)
            .filter(
                Request.id == request_id,
                Request.user_id == user_id
            )
            .first()
        )
    
        if not request:
            raise HTTPException(
                status_code=404,
                detail="Request not found"
            )
    
        db.delete(request)
        db.commit()
    
        return {
            "message": "Request deleted successfully"
        }
    
    @staticmethod
    def delete_all_requests(
        user_id: int,
        db
    ):
    
        deleted_count = (
            db.query(Request)
            .filter(
                Request.user_id == user_id
            )
            .delete(
                synchronize_session=False
            )
        )
    
        db.commit()
    
        return {
            "message": "Requests deleted successfully",
            "deleted_count": deleted_count
        }
    
    @staticmethod
    def delete_failed_requests(
        user_id,
        db
    ):
    
        deleted_count = (
            db.query(Request)
            .filter(
                Request.user_id == user_id
            )
            .filter(
                (Request.status_code == 0)
                |
                (Request.status_code >= 400)
            )
            .delete(
                synchronize_session=False
            )
        )
    
        db.commit()
    
        return {
            "message": "Failed requests deleted successfully",
            "deleted_count": deleted_count
        }
    
                
    @staticmethod
    def status_distribution(user_id, db):
    
        requests = (
            db.query(Request.status_code)
            .filter(Request.user_id == user_id)
            .all()
        )
    
        result = {
            "2xx": 0,
            "3xx": 0,
            "4xx": 0,
            "5xx": 0,
            "failed": 0
        }
    
        for (status,) in requests:
    
            if status == 0:
                result["failed"] += 1
    
            elif 200 <= status < 300:
                result["2xx"] += 1
    
            elif 300 <= status < 400:
                result["3xx"] += 1
    
            elif 400 <= status < 500:
                result["4xx"] += 1
    
            elif status >= 500:
                result["5xx"] += 1
    
        return result

    @staticmethod
    def top_endpoints(user_id, limit, db):
    
        result = (
            db.query(
                Request.endpoint,
                func.count(Request.id).label("count")
            )
            .filter(Request.user_id == user_id)
            .group_by(Request.endpoint)
            .order_by(func.count(Request.id).desc())
            .limit(limit)
            .all()
        )
    
        return [
            {
                "endpoint": row.endpoint,
                "count": row.count
            }
            for row in result
        ]
    
    @staticmethod
    def response_times(user_id, db):
    
        result = (
            db.query(
                func.date(Request.created_at).label("date"),
                func.avg(Request.response_time)
            )
            .filter(Request.user_id == user_id)
            .group_by(func.date(Request.created_at))
            .order_by(func.date(Request.created_at))
            .all()
        )
    
        return [
            {
                "date": str(row[0]),
                "avg_response_time": round(row[1], 2)
            }
            for row in result
        ]
    
    @staticmethod
    def request_volume(user_id, db):
    
        result = (
            db.query(
                func.date(Request.created_at).label("date"),
                func.count(Request.id)
            )
            .filter(Request.user_id == user_id)
            .group_by(func.date(Request.created_at))
            .order_by(func.date(Request.created_at))
            .all()
        )
    
        return [
            {
                "date": str(row[0]),
                "count": row[1]
            }
            for row in result
        ]
    
    @staticmethod
    def recent_requests(user_id, limit, db):
    
        requests = (
            db.query(Request)
            .filter(Request.user_id == user_id)
            .order_by(Request.created_at.desc())
            .limit(limit)
            .all()
        )
    
        return requests
    


    @staticmethod
    def errors(user_id, db):
    
        result = (
            db.query(
                Request.endpoint,
                func.count(Request.id).label("count")
            )
            .filter(
                Request.user_id == user_id,
                Request.status_code >= 400
            )
            .group_by(Request.endpoint)
            .order_by(func.count(Request.id).desc())
            .all()
        )
    
        return [
            {
                "endpoint": row.endpoint,
                "count": row.count
            }
            for row in result
        ]
    

    @staticmethod
    def slow_endpoints(user_id, limit, db):
    
        result = (
            db.query(
                Request.endpoint,
                func.avg(Request.response_time).label("avg_time")
            )
            .filter(Request.user_id == user_id)
            .group_by(Request.endpoint)
            .order_by(
                func.avg(Request.response_time).desc()
            )
            .limit(limit)
            .all()
        )
    
        return [
            {
                "endpoint": row.endpoint,
                "avg_response_time": round(row.avg_time, 2)
            }
            for row in result
        ]