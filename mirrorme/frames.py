from tkinter import *
from tkinter import ttk
from typing import List
import psutil
import socket
from . import gui_actions
from PIL import ImageTk


def initial_form_frame(app: Tk) -> Frame:
    frame = Frame(app)
    port_label = Label(frame, text="Port:")
    port_label.grid(row=0, column=0, sticky=W, pady=2)

    port_entry = Entry(frame)
    port_entry.insert(0, "8080")
    port_entry.grid(row=0, column=1, sticky=W, pady=2)

    network_label = Label(frame, text="Network:")
    network_label.grid(row=1, column=0, sticky=W, pady=2)

    ips: List[str] = []
    for inf, snics in psutil.net_if_addrs().items():
        for idx, snic in enumerate(snics):
            if snic.family == socket.AF_INET:
                ips.insert(idx, f"{inf}: {snic.address}")

    ips.reverse()
    ip_entry = ttk.Combobox(frame, values=ips[1:])
    ip_entry.current(0)
    ip_entry.grid(row=1, column=1, sticky=W, pady=2)

    action_start_server = gui_actions.create_action_start_server(
        ip_entry,
        port_entry,
    )

    def start_server_and_create_qrcode():
        port = port_entry.get()
        ip = ip_entry.get().split(":")[1].strip()
        link = f"https://{ip}:{port}/"
        action_start_server()
        qr_img = gui_actions.create_qr_code(link)
        frame.destroy()
        image_frame = create_image_frame(app, link, qr_img)
        image_frame.pack()

    start_button = Button(frame, text="Start", command=start_server_and_create_qrcode)
    start_button.grid(row=2, column=0, sticky=W, pady=2)

    return frame


def create_image_frame(app: Tk, link: str, qr_image: ImageTk.PhotoImage) -> Frame:
    frame = Frame(app)
    link_label = Label(frame, text=link)
    link_label.grid(row=2, column=0, sticky=W, pady=2)

    def copy_to_clipboard():
        app.clipboard_clear()
        app.clipboard_append(link)

    copy_button = Button(frame, text="copy", command=copy_to_clipboard)
    copy_button.grid(row=2, column=1, sticky=W, pady=2)

    photo_label = Label(frame)
    photo_label.grid(row=3, column=0, sticky=W, pady=2)
    photo_label.photo_image = qr_image  # type: ignore
    photo_label.configure(image=qr_image)  # type: ignore

    return frame
