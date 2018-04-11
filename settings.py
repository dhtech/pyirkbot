import os
import pysvn
from autoreloader.autoreloader import AutoReloader

class Settings(AutoReloader):

  # Sample config, all options are mandatory
  networks = {
    "dhtech": {"server_address": os.environ["IRC_SERVER"],
           "server_password": os.environ["IRC_SERVER_PASSWORD"],
           "server_port": int(os.environ["IRC_SERVER_PORT"]),
           "ssl": True,
           "nick": "HAL",
           "username": "techbot",
           "realname": "techbot",
           "channels": [[x] for x in os.environ["IRC_CHANNELS"].split(",")],
           },
    }

  admin_network = "dhtech"
  admin_channel = os.environ["ADMIN_CHANNEL"]
  admin_adminnicks = os.environ["ADMIN_NICKS"].split(",")

  trigger = "."

  ldap_base = os.environ["LDAP_BASE"]
  ldap_url = os.environ["LDAP_SERVER"]
  ldap_channels = None

  svn_username = os.environ["SVN_USERNAME"]
  svn_password = os.environ["SVN_PASSWORD"]

  log_svn_channels = None
  log_svn_time_format = "%Y%m%d"
  log_svn_teams = os.environ["SVN_TEAMS"].split(",")

  def log_svn_url(self):
    return "https://doc.tech.dreamhack.se/svn/%s/meetings/%%s/log_%%s.txt" % (
        self.event())

  udp_listen = "0.0.0.0"
  udp_port = 9007
  udp_channel = ("dhtech", os.environ["UDP_CHANNEL"])

  recode_out_default_charset = "utf-8"
  recode_fallback = "utf-8"

  # Plugins that will be loaded on startup from plugins/
  plugins = os.environ['LOAD_PLUGINS'].split(',')

  def event(self):
    # TODO(bluecmd): maybe cache this, or maybe not :-)
    currentevent = self.svn().cat ("https://doc.tech.dreamhack.se/svn/currentevent")
    return currentevent.strip().split("=")[1]

  _svn = None
  def svn(self):
    if self._svn:
      return self._svn
    self._svn = pysvn.Client()
    self._svn.callback_get_login = self._svn_login
    self._svn.callback_ssl_server_trust_prompt = self._svn_ssl_trust
    return self._svn

  def _svn_login(self, realm, username, may_save):
    return True, self.svn_username, self.svn_password, False

  def _svn_ssl_trust(self, trust_dict):
    return True, 1, True
