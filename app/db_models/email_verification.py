from sqlalchemy import Column, Integer, String, DateTime 
from datetime import datetime
from ..db.database import base

class RegistrationOTP(base):
    __tablename__ = "registration_otps"

    id = Column(Integer, primary_key=True)

    email = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )

    otp = Column(
        String(6),
        nullable=False
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False
    )

    attempts = Column(
        Integer,
        default=0,
        nullable=False
    )