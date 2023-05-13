import argparse
from aiohttp import web
import aiohttp
import asyncio
import websockets

async def handle(request):
    if request.method == 'GET':
        return web.Response(text='Please use POST method instead of GET')

    if request.method == 'POST':
        payload = await request.text()

        async with websockets.connect(request.app['ws_url']) as websocket:
            await websocket.send(payload)
            try:
                ws_response = await asyncio.wait_for(websocket.recv(), timeout=5)
            except asyncio.TimeoutError:
                ws_response = 'No response received in 5 seconds'

        return web.Response(text=ws_response)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('ws_url', help='The WebSocket URL to connect to')
    parser.add_argument('port', type=int, help='The port number to start the HTTP server on')
    return parser.parse_args()

async def main():
    args = parse_arguments()
    app = web.Application()
    app['ws_url'] = args.ws_url
    app.router.add_route('*', '/', handle)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, '0.0.0.0', args.port)
    await site.start()
    print(f'Serving on port {args.port}')
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())