from fastapi import FastAPI, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from datetime import datetime
from typing import List

# ========================
# CONFIGURATION SECTION
# ========================
SENDER_EMAIL = "gjsabuhurira@gmail.com"
SENDER_PASSWORD = "mnot vqla mhgc zsxg"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
COMMITTEE_EMAILS = [
    "gjsabuhurira@gmail.com",
    "abuhurairagjs@gmail.com",
    "rajesherode2004@gmail.com",
    "rajubairajesh5@gmail.com"
]
# mkxb cpmb nzio sddl
app = FastAPI(
    title="Anti-Ragging Reporting System API",
    description="API for submitting anti-ragging complaints.",
)
app.add_middleware(
   CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
class ComplaintForm(BaseModel):
    register_number: str = Field(..., min_length=0, description="Student's register number.")
    complaint_text: str = Field(..., min_length=0, description="Details of the complaint.")


def send_complaint_email(register_number: str, complaint_text: str, recipients: List[str]):
    """
    Send a complaint email to all committee members.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['Subject'] = f"Ragging Report from (Register number) {register_number}"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = f"""
ANTI-RAGGING COMPLAINT REPORT
=============================

Student Register Number: {register_number}
Complaint Submitted On: {timestamp}

COMPLAINT DETAILS:
{complaint_text}

=============================
This is an automated message from the College Anti-Ragging Reporting System.
Please take immediate action as required.
        """
        msg.attach(MIMEText(body, 'plain'))

        context = ssl.create_default_context()

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SENDER_EMAIL, SENDER_PASSWORD)

            for email in recipients:
                msg['To'] = email
                server.send_message(msg)
                del msg['To']

        print("Email sent successfully!")
        return True

    except smtplib.SMTPAuthenticationError:
        print("Email authentication failed.")
        return False
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {str(e)}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False


@app.post("/submit_complaint", status_code=200)
async def submit_complaint(
        background_tasks: BackgroundTasks,
        register_number: str = Form(..., min_length=0),
        complaint_text: str = Form(..., min_length=0),
):
    """
    Endpoint to receive and process a new anti-ragging complaint.
    """
    try:
        # Pydantic validation is handled by FastAPI's Form(...) parameters

        # Add the email sending task to the background
        background_tasks.add_task(
            send_complaint_email,
            register_number,
            complaint_text,
            COMMITTEE_EMAILS
        )

        return {
            "status": "success",
            "message": "Complaint received. Email is being sent in the background.",
            "register_number": register_number,
            "complaint message": complaint_text
        }

    except Exception as e:
        # Return a 500 Internal Server Error if something goes wrong
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")