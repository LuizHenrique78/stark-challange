import asyncio
import uvicorn
from fastapi import FastAPI
from app.api.v1.endpoints import invoice_callback as webhooks
from app.core.database import engine
from app.models.invoice import Base as InvoiceBase
from app.models.transfer import Base as TransferBase
from app.workers.invoice_scheduler import schedule_invoices_every_3h_for_24h

app = FastAPI(
    title="Stark Bank Challenge API",
    description="Simple FastAPI application issuing invoices and handling callbacks.",
    version="1.0.0"
)

app.include_router(webhooks.router, prefix="/api/v1", tags=["Webhooks"])

# @app.on_event("startup")
# async def startup_event():
#     # Create DB tables if not exist
#     InvoiceBase.metadata.create_all(bind=engine)
#     TransferBase.metadata.create_all(bind=engine)
#
#     # Schedule invoice issuance in the background
#     # In production, you might skip or do a separate scheduling approach:
#     asyncio.create_task(schedule_invoices_every_3h_for_24h())

@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to Stark Bank Challenge API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)