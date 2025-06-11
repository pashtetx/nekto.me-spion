from abc import ABC
from typing import Dict
from client import Client

from utils import generate_random_id

import structlog
import asyncio

class BaseChat(ABC):
    
    def add_member(self, client: Client) -> None:
        ...

    async def start(self) -> None:
        ...

class Chat(BaseChat):
    def __init__(self):
        self.members = list()
        self.messages_buffer = dict()

        self.logger = structlog.get_logger()

    def get_logger(self, client: Client):
        return self.logger.bind(token=client.token[:10])

    def add_member(self, client: Client):
        self.logger.debug("Add client to chat members...", client=client)
        self.members.append(client)
        client.add_event_handler("messages.new", self.on_message)
        client.add_event_handler("dialog.opened", self.on_dialog_opened)
        client.add_event_handler("dialog.closed", self.on_dialog_closed)
        client.add_event_handler("auth.successToken", self.on_auth)
        client.add_event_handler("dialog.typing", self.on_typing)
        self.messages_buffer[client] = list()
        self.logger.debug("Added client to members list", client=client, members=self.members)

    async def on_typing(self, data: Dict[str, any], client: Client) -> None:
        log = self.get_logger(client)
        for member in self.members:
            log.debug(f"Sending typing event to client.", typing=data.get("typing"))
            if member.id == client.id: 
                log.debug(f"Member is client, *skip*")
                continue
            if not hasattr(member, "dialog_id"): 
                log.debug(f"Member has not opened dialog!")
                continue
            payload = {
                "action":"dialog.setTyping",
                "dialogId":member.dialog_id,
                "voice":data.get("voice"),
                "typing":data.get("typing")
            }
            log.debug("Member sent the typing event", payload=payload)
            await member.emit("action", data=payload)

    async def on_auth(self, _, client: Client) -> None:
        log = self.get_logger(client)
        if hasattr(client, "dialog_id"):
            log.debug("Client has open dialog.")
            payload = {
                "action":"anon.leaveDialog",
                "dialogId":client.dialog_id
            }
            log.debug("Client close current dialog!")
            await client.emit(
                "action",
                data=payload, 
            )
        log.debug("Client begins searching the dialog.")
        print(f"[{client.token[:10]}] Ищу собеседника")
        await client.search()

    async def on_message(self, data: Dict[str, any], client: Client) -> None:
        log = self.get_logger(client)
        payload = {
            "action":"anon.readMessages",
            "dialogId":client.dialog_id,
            "lastMessageId":data.get("id")
        }
        await client.emit("action", payload)
        log.debug("Client reads messages.")
        message = data.get('message')
        sender = data.get("senderId")
        if client.id == sender: return
        print(f"[{client.token[:10]}]: {message}")
        self.messages_buffer[client].append(message)
        log.debug("Add message to messages buffer.", message=message, messages_buffer=self.messages_buffer)
        for member in self.members:
            log.debug(f"Sending message to client.")
            if member.id == client.id: 
                log.debug(f"Member is client, *skip*")
                continue
            if not hasattr(member, "dialog_id"): 
                log.debug(f"Member has not opened dialog!")
                continue
            payload = {
                "action":"anon.message",
                "dialogId":member.dialog_id,
                "randomId":generate_random_id(),
                "message":data.get("message"),
                "fileId":None,
            }
            log.debug("Member sent the message.")
            await member.emit("action", data=payload)

    async def on_dialog_opened(self, data: Dict[str, any], client: Client) -> None:
        print(f"[{client.token[:10]}] Нашел собеседника!")
        log = self.get_logger(client)
        log.debug("Client found the dialog.", data=data)
        for member, messages in self.messages_buffer.items():
            if member == client:
                continue
            log.debug("Member will receive messages from the messages buffer", messages=messages, member=member)
            for message in messages:
                payload = {
                    "action":"anon.message",
                    "dialogId":member.dialog_id,
                    "randomId":generate_random_id(),
                    "message":message,
                    "fileId":None,
                }
                await member.emit("action", data=payload)

    async def on_dialog_closed(self, _: Dict[str, any], client: Client) -> None:
        print(f"[{client.token[:10]}] Закрыл диалог.")
        log = self.get_logger(client)
        log.debug("Client closed dialog.")
        self.messages_buffer[client].clear()
        for member in self.members:
            if not hasattr(member, "id"):
                continue
            if member.id == client.id: 
                continue
            if not hasattr(member, "dialog_id"):
                continue
            payload = {
                "action":"anon.leaveDialog",
                "dialogId":member.dialog_id,
            }
            self.messages_buffer[member].clear()
            await member.emit("action", data=payload)
        log.debug("Client begins searching new dialog.")
        await client.search()

    async def start(self) -> None:
        for member in self.members:
            await member.connect()
        await asyncio.gather(
            *[client.wait() for client in self.members]
        )