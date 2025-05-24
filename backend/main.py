from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
from langchainbot.bot import ask_groq

app = FastAPI()
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    answer = ask_groq(request.message)
    return {"response": answer}
