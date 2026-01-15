from fastapi import FastAPI

from pkg.controller.email_controller import router as email_router

app = FastAPI(title="Email Service", version="1.0.0")

app.include_router(email_router)

@app.get("/health", summary="Healthcheck del servizio")
async def health() -> dict:
    return {"status": "ok"}