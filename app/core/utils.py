import secrets
import string
from fastapi_mail import MessageSchema, MessageType, FastMail
from fastapi import UploadFile
from app.core.schemas import EmailSchema
from app.core.config import email_conf
import re
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


async def send_mail(email: EmailSchema):
    """
    Sends an email using the provided email schema.
    Args:
        email (EmailSchema): An instance of EmailSchema containing the email details such as subject, recipients, body, and template name.
    Returns:
        None
    Raises:
        Any exceptions raised by the FastMail send_message method.
    """

    message = MessageSchema(
        subject=email.subject,
        recipients=email.email,
        template_body=email.body,
        subtype=MessageType.html,
    )

    fm = FastMail(email_conf)
    await fm.send_message(message, template_name=f"{email.template_name}.html")


def generate_token(length: int) -> str:
    """
    Generate a random token of specified length.
    This function creates a token consisting of random letters (both uppercase and lowercase)
    and digits. The length of the token is determined by the input parameter.
    Args:
        length (int): The length of the token to be generated.
    Returns:
        str: A randomly generated token of the specified length.
    """
    alphabet = string.ascii_letters + string.digits

    token = "".join(secrets.choice(alphabet) for _ in range(length))

    return token


def validate_email(email: str) -> bool:
    EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if re.match(EMAIL_REGEX, email):
        return True

    return False


def check_file_if_image(file: UploadFile) -> bool:
    if file.filename.lower().split(".")[-1] not in ["img", "png", "jpg", "jpeg"]:
        return False
    return True
