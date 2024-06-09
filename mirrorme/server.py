import ssl
import aiohttp_jinja2
import jinja2
import os
from aiohttp import web
from . import webrtc
from .generate_ssl import create_ssl_context
import asyncio


async def index_handler(request: web.Request) -> web.Response:
    response = aiohttp_jinja2.render_template("index.j2", request, context={})
    return response


def start_server(port: int, ip: str):
    async_loop = asyncio.new_event_loop()
    app = web.Application()
    app.on_shutdown.append(webrtc.on_shutdown)
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(
            os.path.join(os.getcwd(), "mirrorme", "templates")
        ),
    )
    app.router.add_static(
        "/static/",
        path=os.path.join(os.getcwd(), "mirrorme", "templates", "static"),
        name="static",
    )
    app.add_routes(
        [web.get("/", index_handler), web.post("/offer", webrtc.offer_handler)]
    )
    handler = app.make_handler(loop=async_loop)
    ssl_context = create_ssl_context(ip)
    asyncio.set_event_loop(async_loop)
    server = async_loop.create_server(
        handler, host="0.0.0.0", port=port, ssl=ssl_context
    )
    async_loop.run_until_complete(server)
    async_loop.run_forever()
    print("server closed")
