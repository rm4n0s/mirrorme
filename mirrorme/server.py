import ssl
import aiohttp_jinja2
import jinja2
import os
from aiohttp import web
from .generate_ssl import generate_selfsigned_cert
from tempfile import NamedTemporaryFile
import asyncio
from aiohttp.web_runner import GracefulExit


async def index(request: web.Request) -> web.Response:
    context = {"current_date": "January 27, 2017"}
    response = aiohttp_jinja2.render_template("index.j2", request, context=context)
    return response


def start_server(port: int, ip: str):
    async_loop = asyncio.new_event_loop()
    app = web.Application()
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
    app.add_routes([web.get("/", index)])
    handler = app.make_handler(loop=async_loop)
    cert_pem, key_pem = generate_selfsigned_cert("localhost", ["0.0.0.0", ip])

    cert_file = NamedTemporaryFile(mode="w+b")
    key_file = NamedTemporaryFile(mode="w+b")
    cert_file.write(cert_pem)
    cert_file.seek(0)
    key_file.write(key_pem)
    key_file.seek(0)
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.check_hostname = False
    ssl_context.load_cert_chain(cert_file.name, key_file.name)

    asyncio.set_event_loop(async_loop)
    server = async_loop.create_server(
        handler, host="0.0.0.0", port=port, ssl=ssl_context
    )
    async_loop.run_until_complete(server)
    async_loop.run_forever()
    print("server closed")
    # web.run_app(app, loop=async_loop, port=port, )

