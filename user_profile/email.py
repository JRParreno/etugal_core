from django.core.mail import EmailMessage
import smtplib
import ssl
import certifi
from etugal_core import settings
from .models import UserProfile
import threading


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        email.content_subtype = "html"
        EmailThread(email).start()

    @staticmethod
    def send_email_with_certifi(subject, message, from_email, recipient_list):
        context = ssl.create_default_context(cafile=certifi.where())  # Create a context with certifi's CA bundle
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls(context=context)
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(from_email, recipient_list, f'Subject: {subject}\n\n{message}')

