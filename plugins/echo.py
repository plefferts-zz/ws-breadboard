import logging

def onConnection(client):
    logging.debug("EchoClient")
    logging.debug(client)

def main(server):
    logging.debug("Echo")
    server.on('connection', onConnection)