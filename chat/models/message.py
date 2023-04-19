import datetime as datetime
from pydantic import BaseModel, Field
import enum
from datetime import datetime


class Message(BaseModel):
    text: str
    datetime: datetime

    class Config:
        frozen = True
