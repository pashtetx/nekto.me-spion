import asyncio
from client import Client
from dispatcher import Notice, MessagesNewEvent, DialogClosedEvent, DialogOpenedEvent
from mixins.client import SendAnonMessageAction, MessagesReadAction, LeaveDialogAction
from utils import generate_random_id

class MITM:

    def __init__(self):
        self.clients = list()

    async def start(self) -> None:
        await asyncio.gather(*[client.start() for client in self.clients])

    async def on_dialog_opened(self, _: Client, notice: Notice) -> None:
        interlocutors = notice.data["interlocutors"]
        for client in self.clients:
            if client.user_data["id"] not in interlocutors:
                break
        else:
            await client.send_action(LeaveDialogAction(dialogId=notice.data["id"]))

    async def on_message(self, _: Client, notice: Notice) -> None:
        sender = notice.data["senderId"]
        message = notice.data["message"]
        if sender not in list([client.user_data["id"] for client in self.clients]):
            print(f"{sender}: {message}")
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
                dialog_id = other_client.dialog["id"]
                random_id = generate_random_id()
                await other_client.send_action(SendAnonMessageAction(dialogId=dialog_id, randomId=random_id, message=message))

    async def on_dialog_close(self, client: Client, _: Notice) -> None:
        print("Закрываю старый чат... ")
        for other_client in self.clients:
            if other_client == client:
                continue
            if hasattr(other_client, "dialog"):
                await other_client.send_action(LeaveDialogAction(dialogId=other_client.dialog["id"]))

    def add_client(self, client: Client) -> None:
        client.dispatcher.add_event(MessagesNewEvent, self.on_message)
        client.dispatcher.add_event(DialogClosedEvent, self.on_dialog_close)
        client.dispatcher.add_event(DialogOpenedEvent, self.on_dialog_opened)
        self.clients.append(client)
        