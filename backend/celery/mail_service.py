import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os

SMTP_SERVER = os.environ.get('MAILHOG_HOST', 'localhost')
SMTP_PORT = 1025
SENDER_EMAIL = 'noreply@housecare.com'
SENDER_PASSWORD = ''

def send_email(to, subject, content):
    msg = MIMEMultipart()
    msg['To'] = to
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg.attach(MIMEText(content,'html'))

    try:
        with smtplib.SMTP(host=SMTP_SERVER, port=SMTP_PORT) as client:
            client.send_message(msg)
            logging.info(f"Email sent successfully to {to}")
            client.quit()
        return True
    except Exception as e:
        logging.error(f"Failed to send email to {to}: {str(e)}")
        return False
