from pydantic import BaseModel


class RunResponse(BaseModel):
    success: bool
    run_id: str
    status: str
    message: str
    topic: dict | None = None
    article: dict | None = None
