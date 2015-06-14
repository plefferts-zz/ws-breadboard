import sys, asyncore

from tkinter import *
import threading
from time import sleep
from server import Server

class App(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        self.label = StringVar()
        self.widgets(master)

    def widgets(self, root):
        w = Label(root, textvariable=self.label)
        w.grid(row=0, column=0)

        def quit():
            server_thread.stop()
            server_thread.join()
            root.quit()

        def eventQuit(event):
            quit()

        root.protocol("WM_DELETE_WINDOW", quit)
        root.bind('<Command-q>', eventQuit)
        root.bind('<Destroy>', eventQuit)

        # create a toplevel menu
        menubar = Menu(root)

        menu = Menu(menubar, name='apple')
        # not sure how to remove or replace 
        # the existing "Quit" option
        menu.add_command(label="Quit", command=quit, accelerator="Command-q")
        menubar.add_cascade(label="Python", menu=menu)
        
        root.config(menu=menubar)

        self.label.set("Loading...")

root = Tk()
root.title("PyWsServer")
root.resizable(width=FALSE, height=FALSE)
root.geometry('{}x{}'.format(400, 150))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
app = App(root)

class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.server = Server('127.0.0.1', 3000)

    def stop(self):
        app.label.set("The server is shutting down...")
        self.server.close()
        self.join()

    def run(self):
        app.label.set("The server is running.")
        asyncore.loop()

server_thread = ServerThread()
server_thread.start()

root.mainloop()
server_thread.stop()
server_thread.join()
sys.exit()