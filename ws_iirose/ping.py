import asyncio


async def ping_iirose(websocket):
    try:
        while True:
            await websocket.send('')
            await websocket.send(">#")
            await asyncio.sleep(60)
    except:
        pass
