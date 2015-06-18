import socket, asyncore, asynchat, json, logging, sys, traceback
from websocket import WebSocketConnection

class PubSub(list):
    def __call__(self, *args, **kwargs):
        for f in self:
            try:
                f(*args, **kwargs)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logging.error(exc_type)
                logging.error("line: " + str(exc_traceback.tb_lineno))
                logging.error("".join(traceback.format_tb(exc_traceback)))

    def __repr__(self):
        return "PubSub(%s)" % list.__repr__(self)

class HasEvents:
    def __init__(self, *args, **kwargs):
        self.events = {}

    def event(self, name):
        if name not in self.events:
            self.events[name] = PubSub()
        return self.events[name]
    
    def on(self, name, listener):
        self.event(name).append(listener)

    def off(self, name, listener):
        self.event(name).remove(listener)

class Server(asyncore.dispatcher, HasEvents):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        HasEvents.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accepted(self, sock, addr):
        print('Incoming connection from %s' % repr(addr))
        handler = Connection(sock, addr, self)

        def cb():
            handler.off('handshake_complete', cb)
            self.event('connection')(handler)
        
        handler.on('handshake_complete', cb)

class Connection(WebSocketConnection, HasEvents):
    def __init__(self, sock, addr, server):
        WebSocketConnection.__init__(self, sock, addr)
        HasEvents.__init__(self)
        self.server = server

    def handshake_complete(self):
        WebSocketConnection.handshake_complete(self)
        self.event('handshake_complete')()
    
    def handle_utf8_message(self, data):
        try:
            data       = str(data, encoding='utf8')
            event      = json.loads(data)
            event_name = event['_event']
            if event_name in self.events:
                self.events[event_name](event)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(exc_type)
            logging.error("line: " + str(exc_traceback.tb_lineno))
            logging.error("".join(traceback.format_tb(exc_traceback)))

    def send_json(self, val):
        msg = json.dumps(val)
        self.send_utf8_message(bytes(msg, encoding='utf8'))

