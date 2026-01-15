from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo
# Import corretto per la struttura pkg
from pkg.model.email_type import EmailType


class SendEmailRequest(BaseModel):

    emailType: EmailType
    to: EmailStr
    userName: str
    reservationId: str
    returnId: str

    @field_validator("reservationId")
    @classmethod
    def validate_reservation_for_reserve(cls, v: str, info: ValidationInfo) -> str:
        email_type = info.data.get("emailType")
        # Se è RESERVE, la stringa non può essere vuota
        if email_type == EmailType.RESERVE and not v:
            raise ValueError("reservationId cannot be empty when emailType is RESERVE")
        return v

    @field_validator("returnId")
    @classmethod
    def validate_return_for_return(cls, v: str, info: ValidationInfo) -> str:
        email_type = info.data.get("emailType")
        # Se è RETURN, la stringa non può essere vuota
        if email_type == EmailType.RETURN and not v:
            raise ValueError("returnId cannot be empty when emailType is RETURN")
        return v