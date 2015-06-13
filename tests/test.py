import unittest, os, sys, time
sys.path.append(os.path.abspath('.'))

from asynchat_poller             import AsynchatPoller
from ws4py.client.threadedclient import WebSocketClient
from ws4py                       import format_addresses
from dummy_server                import DummyServer

hello_utf8   = "Hello"
hello_binary = b"\x00HelloBinary"

class DummyClient(WebSocketClient):
    def __init__(self, url):
        WebSocketClient.__init__(self, url)
        self.num_messages      = 2
        self.messages_received = []

    def opened(self):

        self.send(hello_utf8)
        self.send(hello_binary, True)

    # def closed(self, code, reason=None):
    #     print("Closed down", code, reason)

    def received_message(self, m):

        if m.is_text:
            self.messages_received.append(str(m))

        if m.is_binary:
            self.messages_received.append(m.data)

        if self.num_messages == len(self.messages_received):
            self.close()


class TestConnection(unittest.TestCase):

    def setUp(self):
        self.server = DummyServer('127.0.0.1', 3000)
        self.async_poller = AsynchatPoller()
        self.async_poller.start()

    def tearDown(self):
        self.server.close()
        self.async_poller.stop()

    def test_connection(self):

        client = DummyClient('ws://127.0.0.1:3000/')

        client.connect()
        time.sleep(.1)

        self.assertEqual(client.messages_received[0], hello_utf8)
        self.assertEqual(client.messages_received[1], hello_binary)
        
        client.close()

if __name__ == '__main__':
    unittest.main()