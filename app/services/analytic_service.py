from sqlalchemy import func
from typing import Annotated
from ..db_models.user import user
from ..db_models.requests import Request


class analytics_service:

    @staticmethod
    def analytics(api_key: str, db):

        existing_user = (
            db.query(user)
            .filter(user.api_key == api_key)
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
                Request.user_id == existing_user.id,
                Request.status_code >= 400
            )
            .count()
        )

        return {
            "total_requests": total_requests,
            "avg_response_time": avg_response_time,
            "success_requests": success_requests,
            "failed_requests": failed_requests
        }
    
    @staticmethod

    def get_requests(user_id:int , search:str , status_code:int, cursor : int , limit:int , db):
        search_req = (
            db.query(Request)
            .filter(Request.user_id == user_id)
        )

        if search :
            search_req = search_req.filter(Request.endpoint.ilike(f"%{search}%"))

        if status_code :
            search_req = search_req.filter(Request.status_code == status_code)


        if cursor:
            search_req = search_req.filter(Request.id > cursor).order_by(Request.id)
                
        search_req = search_req.limit(limit)


        return search_req.all()

        


