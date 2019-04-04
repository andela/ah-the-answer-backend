from datetime import datetime, timedelta
import jwt
from django.conf import settings
from rest_framework import exceptions

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_verification_email(host_email, to, email_subject, content):
    message = Mail(
        from_email=host_email,
        to_emails=to,
        subject=email_subject,
        html_content=content)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        return response
    except Exception:
        return False