from tkinter import *
import segno
import io
from PIL import Image as ImagePIL, ImageTk
import threading
from . import server
import os


def create_action_start_server(ip_entry: Entry, port_entry: Entry):
    def action_start_server():
        port = port_entry.get()
        ip = ip_entry.get().split(":")[1].strip()
        print(f"{port} {ip}")
        server_thread = threading.Thread(
            target=server.start_server,
            args=(
                int(port),
                ip,
            ),
        )
        server_thread.start()

    return action_start_server


def create_qr_code(link: str) -> ImageTk.PhotoImage:
    qrcode = segno.make(link)
    out = io.BytesIO()
    qrcode.save(out, scale=15, kind="png")
    out.seek(0)
    img = ImagePIL.open(out)

    return ImageTk.PhotoImage(image=img)


def action_quit():
    print("quit")
    os._exit(0)
