from socketio import AsyncClient

from typing import Callable, Dict, Any, List, Self, Literal

import structlog
import time

SEX_ANNOTATION = Literal["F", "M"]

class Client(AsyncClient):
    """
    NektoMe SocketIO Async Client
    """

    addr: str = "wss://im.nekto.me"

    def __init__(
        self, 
        token: str, 
        ua: str,
        locale: str = "ru",
        tz: str = "Europe/Kiew",
        age: List[int] = None,
        wish_age: List[List[int]] = None,
        sex: SEX_ANNOTATION = None,
        wish_sex: SEX_ANNOTATION = None,
        role: bool = None,
        wish_role: Literal["suggest", "search"] = None,
        adult: bool = None,
        *args, 
        **kwargs
    ):
        self.token = token
        self.ua = ua
        self.locale = locale
        self.tz = tz

        self.events = dict()

        self._logger = structlog.get_logger()

        super().__init__(*args, **kwargs)

        if role and adult:
            self.get_logger().warning("Adult and Role cannot be True. Choose one!")
        if role and (age or wish_age):
            self.get_logger().warning("Age is not required when you use Role!")

        if not role and wish_role:
            self.get_logger().warning("Wish role is not required when you use not Role!")
            
        self.search_parameters = {
            "wishAge":wish_age,
            "myAge":age,
            "mySex":sex,
            "wishSex":wish_sex,
            "adult":adult,
            "role":role
        }

        if role:
            if wish_role == "suggest":
                self.search_parameters["myAge"] = [30, 40]
            elif wish_role == "search":
                self.search_parameters["myAge"] = [10, 20]
            else:
                self.get_logger().warning("Wish role is unexcepted.", wish_role=wish_role)

        self.on("connect", self.on_connect)
        self.on("disconnect", self.disconnect)
        self.on("notice", self.on_notice)
        self.add_event_handler("auth.successToken", self.on_auth)
        self.add_event_handler("dialog.opened", self.on_dialog_opened)
        self.add_event_handler("dialog.closed", self.on_dialog_closed)
        self.add_event_handler("error.code", self.error_handler)

    def get_logger(self):
        return self._logger.bind(token=self.token[:10])

    async def error_handler(self, data: Dict[str, Any], _: Self) -> None:
        self.get_logger().warning("Unexcepted error", data=data)

    async def on_auth(self, data: Dict[str, Any], _: Self) -> None:
        self.get_logger().debug("The client has logged in.")
        setattr(self, "id", data.get("id"))
        dialog_id = data.get("statusInfo").get("anonDialogId")
        if dialog_id: setattr(self, "dialog_id", dialog_id)

    async def on_connect(self) -> None:
        self.get_logger().debug(f"User has connected!")
        payload = {
            "token":self.token,
            "locale":self.locale,
            "t":round(time.time() * 1000),
            "timeZone":self.tz,
            "version":12,
            "action":"auth.sendToken"
        }
        await self.emit("action", data=payload)
        self.get_logger().debug("Sent user credentials!", payload=payload)

    async def on_dialog_opened(self, data: Dict[str, Any], _: Self) -> None:
        setattr(self, "dialog_id", data.get("id"))
    
    async def on_dialog_closed(self, data: Dict[str, Any], _: Self) -> None:
        delattr(self, "dialog_id")

    def get_handlers(self, name: str) -> List[Callable]:
        self.get_logger().debug(f"Getting {name} handlers!")
        handlers = self.events.get(name) or []
        self.get_logger().debug(f"Found {len(handlers)} handler(s)!")
        return handlers
    
    async def search(self) -> None:
        payload = {
            "action":"search.run"
        }
        payload.update(self.search_parameters)
        self.get_logger().debug("Searching with search parameters", payload=payload)
        await self.emit("action", data=payload)

    async def on_disconnect(self) -> None:
        self.get_logger().debug(f"User has disconnected! token={self.token[:6]}, ua={self.ua[:6]}")
        handlers = self.get_handlers("disconnect")
        if not handlers: return
        for handler in handlers:
            await handler()
        delattr(self, "id")

    async def on_notice(self, data: Dict[str, Any]) -> None:
        self.get_logger().debug("Received notice!", notice=data)
        notice = data.get("notice")
        if not notice: return
        handlers = self.get_handlers(notice)
        if not handlers: return
        for handler in handlers:
            await handler(data.get("data"), self)

    async def connect(self) -> None:
        await super().connect(
            url=self.addr, 
            headers={"User-Agent":self.ua}, 
            transports=["websocket"],
        )

    def add_event_handler(self, event: str, callback: Callable) -> None:
        if not isinstance(self.events.get(event), list):
            self.events[event] = list()
        self.events[event].append(callback)