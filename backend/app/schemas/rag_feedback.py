from pydantic import BaseModel, Field, field_validator

class RAGFeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: int

    @field_validator("rating")
    def validate_rating(cls, v):
        if v not in (1, -1):
            raise ValueError("Rating must be 1 (thumbs up) or -1 (thumbs down)")
        return v
