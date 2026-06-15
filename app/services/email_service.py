import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..core.settings import settings


def send_registration_otp(
    email: str,
    otp: str
):

    message = MIMEMultipart()

    message["From"] = settings.SMTP_EMAIL
    message["To"] = email
    message["Subject"] = "RequestVault Verification Code"

    html = f"""
    <div style="font-family:Arial,sans-serif">

        <h2>RequestVault Email Verification</h2>

        <p>Your verification code is:</p>

        <h1>{otp}</h1>

        <p>
            This code expires in 5 minutes.
        </p>

    </div>
    """

    message.attach(
        MIMEText(
            html,
            "html"
        )
    )

    
    try:
        ip = socket.gethostbyname("smtp.gmail.com")
        print("SMTP IP:", ip)
    except Exception as e:
        print("DNS ERROR:", str(e))
    

    with smtplib.SMTP(
        "smtp.gmail.com",
        465
    ) as server:

        server.starttls()

        server.login(
            settings.SMTP_EMAIL,
            settings.SMTP_PASSWORD
        )

        server.send_message(message)