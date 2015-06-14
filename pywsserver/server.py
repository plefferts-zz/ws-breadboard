import socket, asyncore, asynchat, json, logging
from websocket import WebSocketConnection

class Server(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accepted(self, sock, addr):
        print('Incoming connection from %s' % repr(addr))
        handler = Connection(sock, addr, self)

class Connection(WebSocketConnection):
    def __init__(self, sock, addr, server):
        WebSocketConnection.__init__(self, sock, addr)
        self.server = server
        self.events = {}

    def event(self, name):
        if name not in self.events:
            self.events[name] = PubSub()
        return self.events[name]

    def handshake_complete(self):
        WebSocketConnection.handshake_complete(self)
        self.event('handshake_complete')()
    
    def handle_utf8_message(self, data):
        data       = str(data, encoding='utf8')
        event      = json.loads(data)
        event_name = event['_event']
        if event_name in self.event:
            self.events[event_name](message)

class PubSub(list):
    def __call__(self, *args, **kwargs):
        for f in self:
            try:
                f(*args, **kwargs)
            except:
                e = sys.exc_info()[0]
                print(e)

    def __repr__(self):
        return "PubSub(%s)" % list.__repr__(self)
