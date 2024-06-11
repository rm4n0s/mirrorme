from tkinter import *
from . import gui_actions, gui_frames


def main():
    app = Tk()
    app.protocol("WM_DELETE_WINDOW", gui_actions.action_quit)
    app.title("Mirrorme")
    app.geometry("1024x800")
    initial_form = gui_frames.initial_form_frame(app)
    initial_form.pack()

    quit_button = Button(app, text="Quit", command=gui_actions.action_quit)
    quit_button.pack(side=BOTTOM)

    app.mainloop()
