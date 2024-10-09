import asyncio

import iirosebot.serve
from iirosebot.API.api_get_config import get_serve
from iirosebot.serve import lxyddice

serve_status = get_serve()


async def http_serve():
    if serve_status['http_api']['enabled']:
        await iirosebot.serve.start_http_api(serve_status['http_api']['host'], serve_status['http_api']['port'])


async def webhook_serve():
    if serve_status['webhook']['enabled']:
        await asyncio.gather(asyncio.create_task(iirosebot.serve.start_webhook(serve_status['webhook']['url'], serve_status['webhook']['time_out'])), asyncio.create_task(iirosebot.serve.start_heartbeat()))


async def websocket_server_serve():
    if serve_status['websocket_server']['enabled']:
        await asyncio.gather(asyncio.create_task(iirosebot.serve.start_websocket_server(serve_status['websocket_server']['host'], serve_status['websocket_server']['port'])))

async def websocket_client_serve():
    if serve_status['websocket_reverse']['enabled']:
        await asyncio.gather(asyncio.create_task(iirosebot.serve.start_websocket_client(serve_status['websocket_reverse'])))


async def serve_init():
    asyncio.create_task(lxyddice())
    await asyncio.gather(asyncio.create_task(http_serve()), asyncio.create_task(webhook_serve()), asyncio.create_task(websocket_server_serve()), asyncio.create_task(websocket_client_serve()))
