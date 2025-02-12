import uvicorn
from fastapi import FastAPI
from app.api.v1.endpoints import invoice_callback as webhooks

app = FastAPI(
    title="Stark Bank Challenge API",
    description="Simple FastAPI application issuing invoices and handling callbacks.",
    version="1.0.0"
)

app.include_router(webhooks.router, prefix="/api/v1", tags=["Webhooks"])


@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to Stark Bank Challenge API"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=80, reload=True)
