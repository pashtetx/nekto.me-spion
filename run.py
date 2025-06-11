from chat import Chat

from config import get_clients, get_debug

import asyncio

async def main() -> None:
    chat = Chat()
    for client in get_clients():
        chat.add_member(client)    
    await chat.start()

if __name__ == "__main__":
    get_debug()
    asyncio.run(main())