#!/usr/bin/env python3
# Based on https://gist.github.com/michaelneu/5bf8b99a904cf8c1fa67aadfaeb741d0

import threading
import socket
import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('proxy.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)


class Relay(threading.Thread):
  def __init__(self, stop_listening, socket_a, socket_b, direction_indicator):
    super().__init__()
    self._stop_listening = stop_listening
    self._socket_a = socket_a
    self._socket_b = socket_b
    self._direction_indicator = direction_indicator
  
  def parse_chunk(self, chunk):
    logger.info('Received {} bytes from client '.format(len(chunk)))
    self.hexdump(chunk)    
    return chunk
  
  def hexdump(self, data, length=16):
    filter = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
    lines = []
    digits = 4 if isinstance(data, str) else 2
    for c in range(0, len(data), length):
        chars = data[c:c+length]
        hex = ' '.join(["%0*x" % (digits, (x)) for x in chars])
        printable = ''.join(["%s" % (((x) <= 127 and filter[(x)]) or '.') for x in chars])
        lines.append("%04x  %-*s  %s\n" % (c, length*3, hex, printable))
    #print(''.join(lines))
    logger.info(''.join(lines))

  def run(self):
    while not self._stop_listening.is_set():
      try:
        data = self._socket_a.recv(1024)
        if not data:
          break

        logger.info("{}{}".format(self._direction_indicator, self.parse_chunk(data)))
        self._socket_b.send(data)
      except RuntimeError as error:
        logger.info(error)
        break

class TcpProxy:
  def __init__(self, port, destination, relay_class=Relay):
    self._destination = destination
    self._relay_class = relay_class

    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._socket.bind(("0.0.0.0", port))

  def listen(self, backlog=100):
    self._socket.listen(backlog)
    stop_event = threading.Event()

    while not stop_event.is_set():
      try:
        client, _ = self._socket.accept()
        logger.info("client connected")
        
        destination_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        destination_socket.connect(self._destination)

        relay_a = self._relay_class(stop_event, client, destination_socket, "in >>\t")
        relay_a.start()

        relay_b = self._relay_class(stop_event, destination_socket, client, "<< out\t")
        relay_b.start()
      except KeyboardInterrupt:
        stop_event.set()

if __name__ == "__main__":
  
  proxy = TcpProxy(9000, ("localhost", 3333))
  proxy.listen()
