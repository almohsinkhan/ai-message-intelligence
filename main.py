from fastapi import FastAPI
from pydantic import BaseModel

from src.pipeline import process_message


app = FastAPI(
    title="AI Message Intelligence",
    description="Privacy-first message classification and information extraction",
)


class MessageRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {
        "name": "AI Message Intelligence",
        "status": "running",
    }


@app.post("/analyze")
def analyze(request: MessageRequest):

    result = process_message(
        message_id="API_MESSAGE",
        message=request.message,
        item_number=1,
    )

    return result
