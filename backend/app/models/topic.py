from pydantic import BaseModel


class TopicCandidate(BaseModel):
    query: str
    country_code: str
    country_name: str
    final_score: float = 0
    increase_percentage: float | None = None
    search_volume: int | None = None
