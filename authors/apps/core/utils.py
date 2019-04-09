from datetime import datetime, timedelta
import jwt
from django.conf import settings
from rest_framework import exceptions

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method not in SAFE_METHODS


def send_verification_email(host_email, to, email_subject, content):
    sg = SendGridAPIClient(apikey=os.getenv('SENDGRID_API_KEY'))
    from_email = Email(email=host_email)
    to_email = Email(email=to)
    subject = email_subject
    content = Content("text/html", content)
    try:
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        return response
    except Exception:
        return False
