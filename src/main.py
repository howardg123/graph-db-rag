from fastapi import FastAPI

from .llm import router

app = FastAPI()

app.include_router(router.llm_router)
