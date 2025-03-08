from typing import Union, Optional
from dataclasses import dataclass

import json

class BaseAction:
    action: str = None

@dataclass
class SendTokenAction(BaseAction):
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

    async def send_action(self, action: BaseAction) -> None:
        payload = ["action", {k: v for k, v in action.__dict__.items() if v != "pass"}]
        await self.send("42" + json.dumps(payload))