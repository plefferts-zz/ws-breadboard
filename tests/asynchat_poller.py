# http://austinhartzheim.me/blog/0/python-unit-tests-asyncore/

import asyncore, threading

class AsynchatPoller(threading.Thread):
    def __init__(self):
        super().__init__()
        self.continue_running = True

    def run(self):
        while self.continue_running:
            asyncore.poll()

    def stop(self):
        self.continue_running = False