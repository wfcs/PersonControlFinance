from pydantic import BaseModel, Field


class AiQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class AiAnswer(BaseModel):
    question: str
    answer: str
    plan_required: str = "premium"
