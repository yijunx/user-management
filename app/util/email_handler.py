# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_email_verification(token: str, user_email: str, user_name: str):
    message = Mail(
        from_email="dialects.io@gmail.com",
        to_emails=user_email,
        subject="email verification",
        html_content=f"""

        <p>Dear {user_name.title()}</p>
        <br>
        <p>Please click below link to verify your email:</p>
        <br>
        <p>f{"https://somedmainnamehere"}/email_verification?token={token}</p>
        
        """,
    )
    try:
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(response.status_code)
        # print(response.body)
        # print(response.headers)
    except Exception as e:
        # raise custom error here saying error handing email
        # server issue...
        raise e


if __name__ == "__main__":
    send_email_verification(
        token="token", user_email="user@email.com", user_name="user_name"
    )
