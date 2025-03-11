from client import Client
from dispatcher import AuthSuccessTokenEvent, Notice, DialogOpenedEvent, DialogClosedEvent

from mixins.client import WebAgentAction, SearchRunAction, DialogInfoAction
from utils import generate_webagent

from mitm import MITM

from configparser import ConfigParser

import asyncio

config = ConfigParser()
config.read("config.ini")

async def on_auth(client: Client, event: Notice) -> None:
    token = event.data["tokenInfo"]["authToken"]
    user_id = event.data["id"]
    create_time = event.data["tokenInfo"]["createTime"]
    print(f"{client.name} - успешно авторизировался! user_id={user_id}, create_time={create_time}")
    webagent = generate_webagent(token=token, user_id=user_id, create_time=create_time)
    await client.send_action(WebAgentAction(data=webagent))
    print(f"{client.name} - успешно отправлен WebAgent! webagent={webagent}")
    dialog_id = event.data["statusInfo"].get("anonDialogId")
    if dialog_id:
        print(f"{client.name} - уже имеет активный диалог! dialog_id={dialog_id}")
        await client.send_action(DialogInfoAction(dialogId=dialog_id))
    else:
        await client.send_action(client.search_criteries)

async def on_dialog_opened(client: Client, _: Notice) -> None:
    dialog = client.dialog
    print(f"{client.name} - нашел новый чат! dialog_id={dialog.get('id')}")

async def on_closed_dialog(client: Client, _: Notice) -> None:
    await client.send_action(client.search_criteries)

mitm = MITM()

clients = config.get("settings", "clients").split()

for client_name in clients:
    name = f"client/{client_name}"
    ua = config.get(name, "ua")
    token = config.get(name, "token", fallback=None)
    my_age = config.get(name, "my-age", fallback=None)
    my_sex = config.get(name, "my-sex", fallback=None)
    wish_age = config.get(name, "wish-age", fallback=None)
    wish_sex = config.get(name, "wish-sex", fallback=None)
    is_adult = config.getboolean(name, "is-adult", fallback=None)
    role = config.getboolean(name, "role", fallback=None)
    search_criteries = SearchRunAction(
        myAge=list(map(lambda i: int(i), my_age.split(","))),
        mySex=my_sex,
        wishSex=wish_sex,
        wishAge=list(map(lambda i: list(map(lambda j: int(j), i.split(","))), wish_age.split(" "))),
    )
    if role: search_criteries.role = role
    if is_adult: search_criteries.isAdult = is_adult
    client = Client(name=client_name, token=token, ua=ua, search_criteries=search_criteries)
    client.dispatcher.add_event(AuthSuccessTokenEvent, on_auth)
    client.dispatcher.add_event(DialogOpenedEvent, on_dialog_opened)
    client.dispatcher.add_event(DialogClosedEvent, on_closed_dialog)
    mitm.add_client(client)

if __name__ == "__main__":
    asyncio.run(mitm.start())