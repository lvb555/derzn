"""
Сервис отправки уведомлений
"""

from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from smtplib import SMTPException

def send_email(from_address, to_address, subject, html_message, message):
    """
    Отправка email писем

    Parameters
    ----------
    from_address : str
        адрес отправителя
    to_address : str
        адрес получателя
    subject : str
        тема письма
    html_message : bool
        формат сообщения
    message : str
        тело письма

    Returns
    -------
    bool
    """

    try:
        validate_email(from_address)
        validate_email(to_address)
    except ValidationError:
        return False

    if not message:
        return False

    if not subject:
        subject = ""

    if not format:
        format = 'text'
    
    try:
        send_mail(
            subject,
            message,
            from_address,
            [to_address],
            fail_silently=True,
            html_message=html_message
        )
    except SMTPException as e:
        print('There was an error sending an email.'+ e)
        return False
    
    return True
