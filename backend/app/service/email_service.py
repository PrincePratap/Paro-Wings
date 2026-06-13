from email.message import EmailMessage
import aiosmtplib

EMAIL_ADDRESS = "princepratapfreelancer@gmail.com"
EMAIL_PASSWORD = "sbtn toqr cbbi zioj"


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
        port=587,
        start_tls=True,
        username=EMAIL_ADDRESS,
        password=EMAIL_PASSWORD,
    )