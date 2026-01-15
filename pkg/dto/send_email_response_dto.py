
from pydantic import BaseModel


class SendEmailResponse(BaseModel):

    message: str

