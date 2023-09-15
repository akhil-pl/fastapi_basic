import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


EMAIL_USERNAME = os.environ['EMAIL_USERNAME']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465  # Use 465 for SSL
