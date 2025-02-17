from pydantic import BaseModel

class Answer(BaseModel):
    token: str
    answer: str