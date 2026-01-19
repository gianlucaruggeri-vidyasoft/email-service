import boto3
import json
import smtplib
import os
import time
from email.mime.text import MIMEText
from pymongo import MongoClient

mongo_client = MongoClient("mongodb://root:pass@mongo:27017/")
db = mongo_client.email_service_db
collection = db.logs_invio

sqs = boto3.client(
    "sqs",
    endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566"),
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)

def get_queue_url():
    while True:
        try:
            response = sqs.get_queue_url(QueueName="prenotazioni-queue")
            return response["QueueUrl"]
        except Exception:
            print("⏳ In attesa della coda SQS...")
            time.sleep(2)

def send_and_log_email(to_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "biblioteca@test.com"
    msg["To"] = to_email

    try:
        smtp_server = os.getenv("MAIL_SERVER", "sandbox.smtp.mailtrap.io")
        smtp_port = int(os.getenv("MAIL_PORT", 2525))
        smtp_user = os.getenv("MAIL_USERNAME")
        smtp_pass = os.getenv("MAIL_PASSWORD")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        
        print(f"✅ Email inviata a {to_email}")
        stato = "SUCCESSO"
    except Exception as e:
        print(f"❌ Errore SMTP: {e}")
        stato = f"ERRORE: {str(e)}"

    log_data = {
        "data_invio": time.strftime("%Y-%m-%d %H:%M:%S"),
        "destinatario": to_email,
        "oggetto": subject,
        "messaggio": body,
        "stato": stato
    }
    collection.insert_one(log_data)
    print("💾 Notifica registrata su MongoDB")

QUEUE_URL = get_queue_url()
print(f"📩 Worker attivo su {QUEUE_URL}...")

while True:
    try:
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )

        if "Messages" in response:
            for message in response["Messages"]:
                notification = json.loads(message["Body"])
                email_data = json.loads(notification["Message"])
                
                print(f"📧 Ricevuta richiesta per: {email_data['to_email']}")
                
                send_and_log_email(
                    to_email=email_data["to_email"],
                    subject=email_data["subject"],
                    body=email_data["body"]
                )

                sqs.delete_message(
                    QueueUrl=QUEUE_URL, 
                    ReceiptHandle=message["ReceiptHandle"]
                )
    
    except Exception as e:
        print(f"⚠️ Errore Worker: {e}")
        time.sleep(2)