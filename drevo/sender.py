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
        validate_email(to_address)
    except ValidationError as e:
        print(e)
        return False

    if message is None:
        print('Error send mail: empty message')
        return False

    if subject is None:
        subject = ""

    if html_message is None:
        html_message = False
    
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
        print('Error send mail: ' + e)
        return False
    
    return True
