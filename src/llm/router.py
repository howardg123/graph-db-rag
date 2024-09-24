from fastapi import APIRouter, Query
from typing import Annotated
from .schemas import Question
from .service import Service

import json

llm_router = APIRouter()


@llm_router.post("/generate_response")
async def generate_response(question: Annotated[Question, Query()] = None):
    response = Service().generate_response(question)
    return {"response": json.loads(response)}


@llm_router.get("/populate_data")
async def populate_data():
    response = Service().populate_data()
    return {"response": response}
