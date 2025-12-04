from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str
    history: List[str] = []

class Source(BaseModel):
    reference_id: str
    title: str
    filename: str

class ChatResponse(BaseModel):
    sources: Optional[List[Source]] = None
    token: Optional[str] = None
    error: Optional[str] = None
