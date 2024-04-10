import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = os.environ.get('SMTP_PORT')
SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')


def send_email(
        body,
        sender='sonofgod1551@gmail.com',
        receiver='sonofgod1551@gmail.com',
):
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = 'Job listing'
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        message.attach(MIMEText(body, 'plain'))

        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = message.as_string()
        server.sendmail(sender, receiver, text)
        print('Email sent successfully')


if __name__ == '__main__':
    send_email()
