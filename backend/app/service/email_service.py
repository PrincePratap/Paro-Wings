from email.message import EmailMessage
import aiosmtplib
import os



EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


async def send_otp_email(receiver_email: str, otp: str):
    message = EmailMessage()

    message["From"] = EMAIL_ADDRESS
    message["To"] = receiver_email
    message["Subject"] = "Email Verification OTP"

    message.set_content(
        f"Your OTP is {otp}. It expires in 5 minutes."
    )

    await aiosmtplib.send(
    message,
    hostname="smtp.gmail.com",
    port=465,
    use_tls=True,
    username=EMAIL_ADDRESS,
    password=EMAIL_PASSWORD,
    timeout=30
)