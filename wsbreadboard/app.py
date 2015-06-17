import configparser, os, traceback
import sys, sysconfig, asyncore, logging, imp
import http.server, socketserver
import webbrowser

from tkinter import *
import tkinter.font
import threading
from time import sleep
from server import Server


configFile = 'ws-breadboard.cfg'
logFile    = 'ws-breadboard.log'
pluginPath = 'plugins'
publicPath = 'public'

# OS X
if sysconfig.get_config_vars()['base'].endswith('Contents/Resources'):
    relative   = os.path.join('..', '..', '..')
    logFile    = os.path.join(relative, logFile)
    configFile = os.path.join(relative, configFile)
    pluginPath = os.path.join(relative, pluginPath)
    publicPath = os.path.join(relative, publicPath)

config = configparser.ConfigParser()
defaultConfig = (
'''[server]
loglevel=critical
port=17080
websocketport=17071
''')

if not os.path.isfile(configFile):
    file = open(configFile, 'w')
    file.write(defaultConfig)
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

if not os.path.exists(pluginPath):
    os.makedirs(pluginPath)

plugins = [os.path.splitext(path)[0] for path in os.listdir(pluginPath) if os.path.splitext(path)[1] == '.py']

if not os.path.exists(publicPath):
    os.makedirs(publicPath)

class WebsocketServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        logging.info('Starting Websocket Server')
        self.server = Server('', config.getint('server', 'websocketport'))
        for plugin in plugins:
            logging.info('Loading plugin:' + plugin)
            imp.load_source(plugin, os.path.join(pluginPath, plugin) + '.py').main(self.server)
        logging.info('Websocket Server started')

    def stop(self):
        logging.info('Stopping Websocket Server...')
        try:
            self.server.close()
        except:
            e = sys.exc_info()[0]
            logging.error(e, exc_info=True)
        logging.info('Stopped Websocket Server')

    def run(self):
        logging.info('Websocket Server is running')

        try:
            asyncore.loop()
        except:
            e = sys.exc_info()[0]
            logging.error(e, exc_info=True)
        logging.info('Websocket Server is stopped')

class WebServerThread(threading.Thread):

    def __init__(self):
        super().__init__()
        logging.info('Starting Webserver')
        handler = http.server.SimpleHTTPRequestHandler
        self.httpd = socketserver.TCPServer(('', config.getint('server', 'port')), handler)
        self.httpd.timeout = 1.5
        self.keep_running = True
        logging.info('Webserver started')

    def stop(self):
        logging.info('Stopping Webserver...')
        self.keep_running = False
        logging.info('Stopped Webserver')

    def run(self):
        logging.info('Webserver is running')
        try:
            while self.keep_running:
                self.httpd.handle_request()
        except:
            e = sys.exc_info()[0]
            logging.error(e, exc_info=True)
        logging.info('Webserver is stopped')

ws_server_thread = WebsocketServerThread()
ws_server_thread.start()

os.chdir(publicPath)

webserver_thread = WebServerThread()
webserver_thread.start()

def stop_servers():
    app.label.set("The server is shutting down...")
    ws_server_thread.stop()
    webserver_thread.stop()

root = Tk()
root.title("Websocket Breadboard")
root.resizable(width=FALSE, height=FALSE)
root.geometry('{}x{}'.format(400, 150))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=4)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=4)

class App(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        self.label = StringVar()
        self.widgets(master)

    def widgets(self, root):

        href = r"http://127.0.0.1:17080"

        w = Label(root, textvariable=self.label)
        w.grid(row=1, column=0)

        #windows: hand2
        link = Label(root, text="Launch App", fg="#00B", cursor="pointinghand")
        
        f = tkinter.font.Font(link, link.cget("font"))
        f.configure(underline = True)
        link.configure(font=f)
        
        link.grid(row=2, column=0)

        def copy():
            root.clipboard_clear()
            root.clipboard_append(href)

        # create a popup menu
        popupmenu = Menu(root, tearoff=0)
        popupmenu.add_command(label="Copy Link Address", command=copy)

        def popup(event):
            popupmenu.post(event.x_root, event.y_root)

        def callback(event):
            if event.state & 4:
                popup(event)
            else:
                webbrowser.open_new(href)
        
        link.bind("<Button-2>", popup)
        link.bind("<Button-1>", callback)

        # create a toplevel menu
        menubar = Menu(root)
        menu = Menu(menubar, name='apple')
        menubar.add_cascade(menu=menu)
        
        root.config(menu=menubar)

        self.label.set("Loading...")

app = App(root)

logging.info('Opening Window')
app.label.set("The server is running.")
try:
    root.mainloop()
except:
    e = sys.exc_info()[0]
    logging.error(e, exc_info=True)

logging.info('Window closed')

stop_servers()

logging.info('Waiting for servers to exit...')

sys.exit()
