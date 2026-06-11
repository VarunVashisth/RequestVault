from ..db_models.user import user
from ..db_models.requests import Request


class capture_service():

    @staticmethod
    def check(api:str, db) :
    
    
        check_user =  (
            db.query(user).filter(user.api_key == api).first()
        )

        return check_user
    
    @staticmethod
    def capture(id:int , endpoint:str , status_code:int , response_time: int , ip:str , user_agent:str ,  method:str , db):


        capture = Request(user_id = id ,ip_address =ip, method = method , endpoint = endpoint , status_code = status_code , useragent = user_agent, response_time = response_time)

        db.add(capture)
        db.commit()
        db.refresh(capture)

        return capture

    



        


