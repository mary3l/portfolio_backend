from typing import Optional

from pydantic import BaseModel

class ProjectCreate(BaseModel):
    title: str
    problem: str
    solution: str
    contribution: str
    type: str
    tools_used: str

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    problem: Optional[str] = None
    solution: Optional[str] = None
    contribution: Optional[str] = None
    type: Optional[str] = None
    tools_used: Optional[str] = None
