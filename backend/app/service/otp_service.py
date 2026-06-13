import random
import os
from email.message import EmailMessage
import aiosmtplib
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


# def generate_otp():
#     return str(random.randint(100000, 999999))


# async def send_otp_email(receiver_email: str, otp: str):
    message = EmailMessage()
    message["From"] = EMAIL_ADDRESS
    message["To"] = receiver_email
    message["Subject"] = "Email Verification OTP"

    message.set_content(
        f"""
        Your OTP is: {otp}

        It will expire in 5 minutes.
        """
    )

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=EMAIL_ADDRESS,
        password=EMAIL_PASSWORD,
    )