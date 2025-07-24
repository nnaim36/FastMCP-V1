from fastapi import FastAPI
from fastmcp import FastMCP
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

load_dotenv()

mcp = FastMCP(
    name="Send-Email",
    host="127.0.0.1",
    port=8002
)

#value retreived from .env file
emailAdress = os.getenv("EMAIL_ADDRESS")
emailPassword = os.getenv("EMAIL_PASSWORD")

def send_email(subject: str, body: str, attachment_path: str = None) -> str:
    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = f"AI Agent <{emailAdress}>"
        msg['To'] = emailAdress

        msg.attach(MIMEText(body, "plain"))

        if attachment_path and os.path.isfile(attachment_path):
            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                msg.attach(part)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(emailAdress, emailPassword)
        server.sendmail(emailAdress, emailAdress, msg.as_string())
        server.quit()

        return 'Email sent successfully with attachment' if attachment_path else 'Email sent successfully'

    except Exception as e:
        return f'unable to send email: {str(e)}'
    
@mcp.tool
def send_personal_email(subject: str, body: str, attachment_path: str = None) -> str:
    """
    Sends self an email. email information in .env file
    """
    return send_email(subject, body, attachment_path)

if __name__ == "__main__":
    mcp.run()

#send_psersonal_email("test email", "hello user this is a test email.")