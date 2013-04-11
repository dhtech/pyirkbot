# coding: utf-8
# Author: Christian Svensson <blue@cmd.nu>
#
# udp_listen = '0.0.0.0'
# udp_port = 9007
# udp_channel = ('dhtech', '#dhtech')

from plugins import Plugin
from settings import Settings
from threading import Thread
import SocketServer

class ThreadedUdpServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
  pass

class UdpHandler(SocketServer.BaseRequestHandler):
  def handle(self):
    if self.server.bot == None:
      return
    data = self.request[0]
    self.server.bot.tell(Settings().udp_channel[0],
        Settings().udp_channel[1], data.strip())

class UdpPlugin(Plugin):
  hooks = ['timer_beat']

  def __init__(self):
    self.thread = None
    self.server = None
    self.bot = None

  def timer_beat(self, bot, now, network):
    self.bot = bot
    self.server.bot = bot

  def on_load(self):
    self.server = ThreadedUdpServer(
        (Settings().udp_listen, Settings().udp_port),
        UdpHandler)
    self.server.bot = self.bot
    self.thread = Thread(target=self.server.serve_forever)
    self.thread.daemon = True
    self.thread.start()

  def on_unload(self):
    self.server.shutdown()
    self.server.server_close()
    self.thread.join()
    self.thread = None

if __name__ == "__main__":
  class Test:
    def tell(self, network, channel, msg):
      print network, channel, msg

  test = Test()
  u = UdpPlugin()
  u.on_load()
  u.on_join(test, None, None, None)

  import time
  time.sleep(1)
  u.on_unload()
  u = UdpPlugin()
  u.on_load()
  u.on_join(test, None, None, None)

  time.sleep(1)
