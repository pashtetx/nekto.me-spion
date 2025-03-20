import asyncio
from client import Client
from dispatcher import Notice, MessagesNewEvent, DialogClosedEvent, DialogOpenedEvent, DialogInfoEvent
from mixins.client import SendAnonMessageAction, MessagesReadAction, LeaveDialogAction
from utils import generate_random_id

class MITM:

    def __init__(self):
        self.clients = list()
        self.message_buffer = dict()

    async def start(self) -> None:
        await asyncio.gather(*[client.start() for client in self.clients])

    async def on_dialog_opened(self, client: Client, _: Notice) -> None:
        for other_client in self.clients:
            if len(self.message_buffer[other_client]) > 0:
                for message in self.message_buffer[other_client]:
                    await self.other_client.send_message(content=message)
            if other_client == client:
                continue
            if hasattr(other_client, "dialog"):
                if other_client.dialog["id"] == client.dialog["id"]:
                    await other_client.send_action(LeaveDialogAction(dialogId=other_client.dialog["id"]))

    async def on_message(self, client: Client, notice: Notice) -> None:
        sender = notice.data["senderId"]
        message = notice.data["message"]
        if sender not in list([client.user_data["id"] for client in self.clients]):
            print(f"({client.name}) {sender}: {message}")
        for other_client in self.clients:
            if other_client.user_data["id"] == sender:
                return
        for other_client in self.clients:
            if other_client.user_data["id"] == sender:
                break
            elif hasattr(other_client, "dialog"):
                if sender in other_client.dialog["interlocutors"]:
                    await other_client.send_action(MessagesReadAction(dialogId=other_client.dialog["id"], lastMessageId=notice.data["id"]))
                    continue
                await other_client.send_message(content=message)
            else:
                print("Send message to buffer, because the client searching...")
                self.message_buffer[other_client].append(message)


    async def on_dialog_close(self, client: Client, _: Notice) -> None:
        print(f"{client.name} - Закрываю старый чат... ")
        for other_client in self.clients:
            self.message_buffer[other_client].clear()
            if other_client == client:
                continue
            if hasattr(other_client, "dialog"):
                await other_client.send_action(LeaveDialogAction(dialogId=other_client.dialog["id"]))

    def add_client(self, client: Client) -> None:
        client.dispatcher.add_event(MessagesNewEvent, self.on_message)
        client.dispatcher.add_event(DialogClosedEvent, self.on_dialog_close)
        client.dispatcher.add_event(DialogOpenedEvent, self.on_dialog_opened)
        client.dispatcher.add_event(DialogInfoEvent, self.on_dialog_opened)
        self.message_buffer[client] = list()
        self.clients.append(client)
        
