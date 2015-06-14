import configparser, os
import sys, sysconfig, asyncore, logging, imp

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

configFile = 'pywsserver.cfg'
logFile    = 'pywsserver.log'
pluginPath = 'plugins'

# OS X
if sysconfig.get_config_vars()['base'].endswith('Contents/Resources'):
    relative   = os.path.join('..', '..', '..')
    logFile    = os.path.join(relative, logFile)
    configFile = os.path.join(relative, configFile)
    pluginPath = os.path.join(relative, pluginPath)

config = configparser.ConfigParser()

if not os.path.isfile(configFile):
    file = open(configFile, 'w')
    file.write("[server]\nloglevel=critical")
    file.close()

config.read(configFile)

logLevel = {
    'debug'    : logging.DEBUG,
    'info'     : logging.INFO,
    'warning'  : logging.WARNING,
    'error'    : logging.ERROR,
    'critical' : logging.CRITICAL
}[config.get('server', 'loglevel')]

logging.basicConfig(filename=logFile, filemode='a', level=logLevel)

plugins = [os.path.splitext(path)[0] for path in os.listdir(pluginPath) if os.path.splitext(path)[1] == '.py']

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
        logging.info('Starting server')
        self.server = Server('127.0.0.1', 3000)
        for plugin in plugins:
            logging.info('Loading plugin:' + plugin)
            imp.load_source(plugin, os.path.join(pluginPath, plugin) + '.py').main(self.server)
        logging.info('Server started')

    def stop(self):
        app.label.set("The server is shutting down...")
        self.server.close()
        self.join()

    def run(self):
        app.label.set("The server is running.")
        logging.info('Listening...')
        asyncore.loop()

server_thread = ServerThread()
server_thread.start()

logging.info('Starting window')
root.mainloop()
logging.info('Window closed')
server_thread.stop()
server_thread.join()
sys.exit()