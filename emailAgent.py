from fastapi import FastAPI
from fastmcp import FastMCP
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP()

#value retreived from .env file
emailAdress = os.getenv("EMAIL_ADDRESS")
emailPassword = os.getenv("EMAIL_PASSWORD")

def send_email(subject: str, body: str) -> str:
    try:
        msg:MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = f"AI Agent <{emailAdress}>"
        msg['To'] = emailAdress

        return 'Email sent succesfully'

    except Exception as e:
        return 'unable to send email :('
    
@mcp.tool
def send_psersonal_email(subject: str,body:str) -> str:
    """
    Sends self an email. email information in .env file
    """
    return send_email(subject, body)

if __name__ == "__main__":
    mcp.run()