from enum import Enum
from pydantic import BaseModel, Field


class ModelEnum(str, Enum):
    llama = "llama"
    openai = "openai"


class Question(BaseModel):
    question: str = Field(
        title="question", description="Question sent to the model.")
    model: ModelEnum = Field(
        title="model", description="Model to use.")
