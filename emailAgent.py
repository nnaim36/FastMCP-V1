from fastapi import FastAPI
from fastmcp import FastMCP
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP(
    name="Send-Email",
    host="127.0.0.1",
    port=8002
)

#value retreived from .env file
emailAdress = os.getenv("EMAIL_ADDRESS")
emailPassword = os.getenv("EMAIL_PASSWORD")

def send_email(subject: str, body: str) -> str:
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = f"AI Agent <{emailAdress}>"
        msg['To'] = emailAdress

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(emailAdress, emailPassword)
        server.sendmail(emailAdress, emailAdress, msg.as_string())
        server.quit()

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

#send_psersonal_email("test email", "hello user this is a test email.")