import unittest, os, sys, time
sys.path.append(os.path.abspath('.'))

from asynchat_poller import AsynchatPoller
from src.echo_server import EchoServer
from ws4py.client import WebSocketBaseClient


class EchoClient(WebSocketBaseClient):
    def handshake_ok(self):
        print("Opening %s" % format_addresses(self))
        m.add(self)

    def received_message(self, msg):
        print(str(msg))

class TestConnection(unittest.TestCase):

    def setUp(self):
        self.server = EchoServer('127.0.0.1', 3000)
        self.async_poller = AsynchatPoller()
        self.async_poller.start()

    def tearDown(self):
        self.server.close()
        self.async_poller.stop()

    def test_connection(self):

        client = EchoClient('ws://127.0.0.1:3000/ws')
        client.connect()

        client.close()
        pass

if __name__ == '__main__':
    unittest.main()