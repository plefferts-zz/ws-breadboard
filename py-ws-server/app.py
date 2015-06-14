from tkinter import *

class App(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        self.widgets()
    
    def widgets(self):
        w = Label(root, text="The server is running.")
        w.grid(row=0, column=0)

        # create a toplevel menu
        menubar = Menu(root)
        menubar.add_command(label="Quit", command=root.quit)

        # display the menu
        root.config(menu=menubar)


root = Tk()
root.title("PyWsServer")
root.resizable(width=FALSE, height=FALSE)
root.geometry('{}x{}'.format(400, 150))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
app = App(root)
root.mainloop()
