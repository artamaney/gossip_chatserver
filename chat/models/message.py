from pydantic import BaseModel
import enum


class MessageType(enum.StrEnum):
    USER_ENTER = "USER_ENTER"
    INIT = "INIT"
    DM = "DM"
    MSG = "MSG"
    USER_LEAVE = "USER_LEAVE"


class Message(BaseModel):
    mtype: MessageType
    id: str
    text: str
    to_id: str
    gossip_id: str

    # timestamp: int

    class Config:
        frozen = True
