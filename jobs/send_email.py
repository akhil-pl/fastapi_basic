import yagmail
from config.config import EMAIL_USERNAME, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT


def sent_email(to_email: str, subject: str, content: str):
    try:
        # Create a yagmail SMTP client
        yag = yagmail.SMTP(EMAIL_USERNAME, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT)

        # Send the email
        yag.send(to=to_email, subject=subject, contents=content)

        return {"message": "Email sent successfully"}
    except Exception as e:
        return {"error": str(e)}
