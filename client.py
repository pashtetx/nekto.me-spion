from websockets import connect as ws_connect

from dispatcher import (
    Dispatcher, 
    Notice, 
    DialogOpenedEvent, 
    AuthSuccessTokenEvent, 
    DialogClosedEvent, 
    DialogInfoEvent, 
    ReadyEvent,
    ErrorCodeEvent
)

from typing import Self

from mixins.client import ClientSendMixin, SendTokenAction, SearchRunAction

from exceptions import NektoMeException

import math
import time
import asyncio
    
class Client(ClientSendMixin):
    ws_addr: str = "wss://im.nekto.me/socket.io/?EIO=3&transport=websocket"

    def __init__(self, token: str, ua: str = None, name: str = None, search_criteries: SearchRunAction = None):
        self.dispatcher = Dispatcher(self)
        self.ua = ua
        self.search_criteries = search_criteries or SearchRunAction()
        self.name = name or token[:6]
        print(f"{self.name} - параметры поиска: ", self.search_criteries)
        self.token = token
        self.dispatcher.add_event(DialogOpenedEvent, self.set_dialog)
        self.dispatcher.add_event(AuthSuccessTokenEvent, self.set_user_data)
        self.dispatcher.add_event(DialogClosedEvent, self.set_dialog)
        self.dispatcher.add_event(DialogInfoEvent, self.set_dialog)
        self.dispatcher.add_event(ReadyEvent, self.on_ready)
        self.dispatcher.add_event(ErrorCodeEvent, self.on_error)

    async def on_error(self, _: Self, notice: Notice) -> None:
        if notice.data["id"] == 400:
            return print(f"Warning: {self.name} - неверный webagent.")
        raise NektoMeException(notice.data["description"])

    async def on_ready(self, client: Self, _: Notice) -> None:
        token = self.token
        t = math.floor(time.time() * 1000)  
        await client.send_action(SendTokenAction(token=token, t=t))

    async def set_dialog(self, _: Self, notice: Notice) -> None:
        if notice.data.get("close"):
            delattr(self, "dialog")
        else:
            self.dialog = notice.data

    async def set_user_data(self, _: Self, notice: Notice) -> None:
        self.user_data = notice.data

    async def heartbeat(self, interval: int = 20) -> None:
        while True:
            await asyncio.sleep(interval)
            await self.send_heartbeat()

    async def start(self) -> None:
        async with ws_connect(self.ws_addr, user_agent_header=self.ua, ping_timeout=10000) as ws:
            asyncio.ensure_future(self.heartbeat())
            self.ws = ws
            async for message in ws:
                await self.dispatcher.handler(message)
            
