from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

# Import aggiornati con prefisso pkg.
from pkg.dto.send_email_request_dto import SendEmailRequest
from pkg.dto.send_email_response_dto import SendEmailResponse
from pkg.service.email_service import EmailSendingError, send_email_via_smtp
from pkg.model.email_type import EmailType
from pkg.repository.reservation_repository import ReservationRepository
from pkg.repository.return_repository import ReturnRepository

router = APIRouter(prefix="/api/internal/emails", tags=["emails"])

reservation_repository = ReservationRepository()
return_repository = ReturnRepository()

async def validate_reservation(request: SendEmailRequest):
    if not await reservation_repository.exists(request.reservationId):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Prenotazione con id {request.reservationId} non trovata",
        )

async def validate_return(request: SendEmailRequest):
    if not await return_repository.exists(request.returnId):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Restituzione con id {request.returnId} non trovata",
        )

VALIDATION_STRATEGIES = {
    EmailType.RESERVE: validate_reservation,
    EmailType.RETURN:  validate_return,
}

@router.post(
    "/send/v1",
    response_model=SendEmailResponse,
    status_code=HTTP_200_OK,
    summary="Invio comunicazione email interna",
)
async def send_email(request: SendEmailRequest) -> SendEmailResponse:

    validator_function = VALIDATION_STRATEGIES.get(request.emailType)

    if validator_function:
        await validator_function(request)

    try:
        await send_email_via_smtp(request)

    except ValueError as ve:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(ve)) from ve
    except EmailSendingError as ese:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ese)) from ese
    except Exception as exc:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore interno durante l'invio dell'email: {str(exc)}",
        ) from exc

    return SendEmailResponse(message="Email inviata con successo")