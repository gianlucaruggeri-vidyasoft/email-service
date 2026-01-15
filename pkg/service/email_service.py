import os
import smtplib
from email.message import EmailMessage
from typing import Tuple, Callable, Dict
from dotenv import load_dotenv

# MODIFICA QUI: Import con prefisso pkg.
from pkg.dto.send_email_request_dto import SendEmailRequest
from pkg.model.email_type import EmailType

load_dotenv()

class EmailSendingError(Exception):
    pass

def _get_reserve_content(payload: SendEmailRequest, user_name: str) -> Tuple[str, str]:
    return (
        "Conferma Prenotazione",
        f"Ciao {user_name},\n\n"
        f"La tua prenotazione {payload.reservationId} è stata confermata.\n\n"
        "Cordiali saluti,\n"
        "Il Team"
    )

def _get_return_content(payload: SendEmailRequest, user_name: str) -> Tuple[str, str]:
    return (
        "Conferma Restituzione",
        f"Ciao {user_name},\n\n"
        f"La restituzione {payload.returnId} è stata registrata.\n\n"
        "Cordiali saluti,\n"
        "Il Team"
    )

EMAIL_STRATEGIES: Dict[EmailType, Callable[[SendEmailRequest, str], Tuple[str, str]]] = {
    EmailType.RESERVE: _get_reserve_content,
    EmailType.RETURN: _get_return_content,
}

def _build_email_subject_and_body(payload: SendEmailRequest) -> Tuple[str, str]:
    # Dato che userName è obbligatorio nel DTO, lo usiamo direttamente
    user_name = payload.userName
    
    strategy = EMAIL_STRATEGIES.get(payload.emailType)
    
    if not strategy:
        raise EmailSendingError(f"Tipo email non supportato: {payload.emailType}")
        
    return strategy(payload, user_name)

async def send_email_via_smtp(payload: SendEmailRequest) -> None:
    smtp_host = os.getenv("MAIL_SERVER")
    try:
        smtp_port = int(os.getenv("MAIL_PORT", "2525"))
    except ValueError:
        smtp_port = 2525
        
    smtp_username = os.getenv("MAIL_USERNAME")
    smtp_password = os.getenv("MAIL_PASSWORD")
    smtp_from = os.getenv("MAIL_FROM", "no-reply@example.com")
    
    subject, body = _build_email_subject_and_body(payload)

    msg = EmailMessage()
    msg["From"] = smtp_from
    msg["To"] = payload.to
    msg["Subject"] = subject
    
    msg.set_content(body, charset='utf-8')

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            
            server.send_message(msg)
            
    except Exception as exc:
        raise EmailSendingError(f"Errore nell'invio dell'email: {exc}") from exc