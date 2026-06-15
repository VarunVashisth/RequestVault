import resend

from ..core.settings import settings

resend.api_key = settings.RESEND_API_KEY



def send_registration_otp(
    email: str,
    otp: str
):

    resend.Emails.send(
        {
            "from": "RequestVault <onboarding@resend.dev>",
            "to": [email],
            "subject": "RequestVault Verification Code",
            "html": f"""
            <div
                style="
                font-family:Arial,sans-serif;
                max-width:600px;
                margin:auto;
                "
            >

                <h2>
                    RequestVault Email Verification
                </h2>

                <p>
                    Your verification code is:
                </p>

                <div
                    style="
                    font-size:32px;
                    font-weight:bold;
                    letter-spacing:4px;
                    margin:20px 0;
                    "
                >
                    {otp}
                </div>

                <p>
                    This code expires in
                    10 minutes.
                </p>

                <p>
                    If you didn't request this,
                    you can ignore this email.
                </p>

            </div>
            """
        }
    )