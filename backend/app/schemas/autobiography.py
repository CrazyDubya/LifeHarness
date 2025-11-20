from typing import Literal, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ViewProfileIn(BaseModel):
    audience: Literal["self", "trusted", "heirs", "public"]
    date: datetime
    include_placeholders: bool = False
    scope: Dict[str, Any]  # e.g., {"type": "full"} or {"type": "time_range","from":1995,"to":2010}
    tone: Literal["light", "balanced", "deep"] = "balanced"


class AutobioOut(BaseModel):
    outline: Dict[str, Any]
    markdown: str
