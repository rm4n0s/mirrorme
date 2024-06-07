from tkinter import *
from tkinter import ttk
import psutil
import socket
from .server import start_server
from PIL import Image as ImagePIL, ImageTk 
import segno
import io 
import threading
import os

port_entry: Entry 
ip_entry: Entry 
photo_label: Label
app: Tk
server_thread: threading.Thread

def action_start_server():
    port = port_entry.get()
    ip = ip_entry.get().split(':')[1].strip()
    print(f'{port} {ip}')
    segno.make_qr
    qrcode = segno.make(f'https://{ip}:{port}/')
    out = io.BytesIO()
    qrcode.save(out, scale=15, kind='png')
    out.seek(0)
    img = ImagePIL.open(out) 
    
    photo_image = ImageTk.PhotoImage(image=img) 
    photo_label.photo_image = photo_image 
    photo_label.configure(image=photo_image) 

    global server_thread
    server_thread = threading.Thread(target=start_server, args=(int(port),ip,))
    server_thread.start()
    # start_server(int(port),ip)

def action_quit():
    print('quit')
    os._exit(0)
    

def main_gui():
    global app
    app = Tk() 
    app.title("Mirrorme")
    app.geometry('800x640')
    port_label = Label(app, text="Port:")
    port_label.grid(row = 0, column = 0, sticky = W, pady = 2)

    global port_entry 
    port_entry = Entry(app)
    port_entry.insert(0, "8080")
    port_entry.grid(row = 0, column = 1, sticky = W, pady = 2)


    network_label = Label(app, text="Network:")
    network_label.grid(row = 1, column = 0, sticky = W, pady = 2)

    ips = []
    for inf, snics in psutil.net_if_addrs().items():
        for idx, snic in enumerate(snics):
            if snic.family == socket.AF_INET:
                ips.insert(idx, f'{inf}: {snic.address}')

    ips.reverse()
    global ip_entry
    ip_entry = ttk.Combobox(app, values=ips[1:])
    ip_entry.current(0)
    ip_entry.grid(row = 1, column = 1, sticky = W, pady = 2)
    

    start_button = Button(app, text="Start", command=action_start_server)
    start_button.grid(row = 2, column = 0, sticky = W, pady = 2)

    quit_button = Button(app, text="Quit", command=action_quit)
    quit_button.grid(row = 2, column = 1, sticky = W, pady = 2)

    global photo_label
    photo_label = Label(app) 
    photo_label.grid(row = 3, column = 0, sticky = W, pady = 2)

    app.mainloop()
