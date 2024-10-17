from django.core.mail import EmailMessage
import threading
import smtplib
import ssl
import certifi
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from etugal_core import settings

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

    @staticmethod
    def send_html_email_with_certifi(subject, plain_message, html_message, from_email, recipient_list):
        """
        Sends an HTML email with a plain text fallback using certifi for SSL/TLS.
        """
        context = ssl.create_default_context(cafile=certifi.where())  # Use certifi's CA bundle

        # Create a MIME Multipart message to support both plain text and HTML content
        msg = MIMEMultipart("alternative")
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = ', '.join(recipient_list)

        # Add plain text part (for fallback)
        part1 = MIMEText(plain_message, "plain")
        msg.attach(part1)

        # Add HTML part
        part2 = MIMEText(html_message, "html")
        msg.attach(part2)

        # Send the email using smtplib with certifi's CA bundle for SSL/TLS security
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls(context=context)
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(from_email, recipient_list, msg.as_string())