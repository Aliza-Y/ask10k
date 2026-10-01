from fastapi import FastAPI
from pydantic import BaseModel
from src.generate.answer import answer_question

app = FastAPI(title="Ask a 10-K API")


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(request: QuestionRequest):
    return answer_question(request.question)