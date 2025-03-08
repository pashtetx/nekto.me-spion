import json

from abc import ABC
from typing import Union, Callable, Optional
from dataclasses import dataclass


@dataclass()
class Notice:
    name: str
    data: str = None


class BaseEvent(ABC):
    """
    BaseEvent from nektome
    """
    name: str = None

    def __init__(self, callback: Callable):
        self.callback = callback


class AuthBaseEvent(BaseEvent):
    """
    Auth event 
    """
    name: str = None

    def __init__(self, callback: Callable):
        self.name = "auth." + self.name
        super().__init__(callback)


class AuthSuccessTokenEvent(AuthBaseEvent):
    name = "successToken"


class ReadyEvent(BaseEvent):
    name: str = "ready"


class DialogBaseEvent(BaseEvent):
    name: str = None

    def __init__(self, callback: Callable):
        self.name = "dialog." + self.name
        super().__init__(callback)


class DialogOpenedEvent(DialogBaseEvent):
    name = "opened"


class DialogClosedEvent(DialogBaseEvent):
    name = "closed"


class DialogInfoEvent(DialogBaseEvent):
    name = "info"


class MessagesNewEvent(BaseEvent):
    name = "messages.new"

class ErrorCodeEvent(BaseEvent):
    name = "error.code"

class BaseEventParser(ABC):
    def parse(self, message: Union[str, bytes]) -> None:
        ...


class NektoMeEventParser(BaseEventParser):
    def parse(self, message: Union[str, bytes]) -> Optional[Notice]:
        if message.startswith("0"):
            return Notice(name="init", data=json.loads(message.strip("0")))
        if message.startswith("40"):
            return Notice(name="ready")
        if not message.startswith("42"):
            return
        data = json.loads(message.strip("42"))
        return Notice(name=data[1]["notice"], data=data[1]["data"])


class Dispatcher:
    """
    Disptacher nektome clients
    """

    def __init__(self, client):
        self.client = client
        self.events = list()
        self.parser = NektoMeEventParser()
    
    async def handler(self, message: Union[str, bytes]) -> None:
        notice = self.parser.parse(message)
        if not notice:
            return
        for event in self.events:
            if notice.name == event.name:
                await event.callback(self.client, notice)

    def add_event(self, event: BaseEvent, callback: Callable) -> None:
        self.events.append(event(callback))