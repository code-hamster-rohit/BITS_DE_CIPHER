from pydantic import BaseModel

class UploadData(BaseModel):
    question_number: int
    answer: str
    rate_of_reduction: float
    base_score: int
    rate_change_factor: float
    hint_1: str
    hint_1_timedelta: int
    hint_2: str
    hint_2_timedelta: int