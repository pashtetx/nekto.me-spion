from typing import Union, Optional, Any
from dataclasses import dataclass

from utils import generate_random_id

import json

@dataclass
class SendTokenAction:
    token: str
    t: int
    action: str = "auth.sendToken"
    version: int = 12

@dataclass
class WebAgentAction:
    data: str
    type: str = "web-agent"

@dataclass
class SearchRunAction:
    myAge: Optional[list]
    mySex: Optional[str] 
    wishSex: Optional[str] 
    wishAge: Optional[list]
    isAdult: Optional[bool] = "pass"
    role: Optional[bool] = "pass"
    action: str = "search.run"
    
@dataclass
class SendAnonMessageAction:
    dialogId: int
    message: str
    randomId: int
    action: str = "anon.message"
    field: str = None

@dataclass
class DialogInfoAction:
    dialogId: int
    action: str = "dialog.info"

@dataclass
class MessagesReadAction:
    dialogId: int
    lastMessageId: int
    action: str = "anon.readMessages"

@dataclass
class LeaveDialogAction:
    dialogId: int
    action: str = "anon.leaveDialog"

class ClientSendMixin:
    """
    ClientMixin for sends messages to nektome
    """

    async def send_heartbeat(self) -> None:
        await self.send("2")

    async def send(self, message: Union[str, bytes]) -> None:
        if not hasattr(self, "ws"):
            raise ValueError("Client is not connected! Please connect client: .start()")
        await self.ws.send(message)

    async def send_action(self, action: Any) -> None:
        payload = ["action", {k: v for k, v in action.__dict__.items() if v != "pass"}]
        await self.send("42" + json.dumps(payload))

    async def send_message(self, content: str) -> None:
        random_id = generate_random_id() 
        dialog_id = self.dialog["id"]
        payload = SendAnonMessageAction(message=content, randomId=random_id, dialogId=dialog_id)
        await self.send_action(payload)

