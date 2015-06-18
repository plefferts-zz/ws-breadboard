from http.server import SimpleHTTPRequestHandler
import socketserver, socket
 
class RequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_cache_headers()
        SimpleHTTPRequestHandler.end_headers(self)
 
    def send_cache_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")

class Server(socketserver.TCPServer):
    def __init__(self,address):
        socketserver.TCPServer.__init__(self, address, RequestHandler)

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)