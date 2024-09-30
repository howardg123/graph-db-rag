from fastapi import APIRouter, Query
from typing import Annotated
from .schemas import Question
from .service import Service

import json

llm_router = APIRouter()


@llm_router.post("/generate_response")
async def generate_response(question: Annotated[Question, Query()] = None):
    response = Service().generate_response(question)
    return {"response": response}


@llm_router.post("/rephrase_prompt")
async def rephrase_prompt(question: Annotated[Question, Query()] = None):
    response = Service().rephrase_prompt(question)
    return {"response": response}


@llm_router.get("/populate_data")
async def populate_data():
    response = Service().populate_data()
    return {"response": response}


@llm_router.get("/delete_data")
async def delete_data():
    response = Service().delete_data()
    return {"response": response}
