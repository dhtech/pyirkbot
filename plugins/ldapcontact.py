# coding: utf-8
# Author: Christian Svensson <blue@cmd.nu>
#
# ldap_url = "ldaps://ldap.se"
# ldap_base = "ou=blah"
# ldap_channels = [ '#mychannel' ]

import re
import sys
import ldap
from commands import Command
from settings import Settings

class LdapcontactCommand(Command):
  def __init__(self):
    self.non_decimal = re.compile(r'[^\d+]+')
    self.international = re.compile(r'^0')

  def on_load(self):
    pass

  def on_unload(self):
    pass

  def _format_phone(self, nr):
    if nr == None:
      return ""
    nr = self.non_decimal.sub('', nr)
    nr = self.international.sub('+46', nr)

    if nr.startswith("+46") and len(nr) == 12:
      return nr[0:3] + " " + nr[3:5] + "-" + nr[5:8] + " " + nr[8:10] + " " \
          + nr[10:12]
    return nr

  def _safe_get(self, entry, key):
    return entry[1][key][0] if key in entry[1] else None

  def trig_contact(self, bot, source, target, trigger, argument, network):
    """.contact (user|filter e.g. givenname=david, sn=andersson, o=cisco)"""
    if Settings().ldap_channels != None and \
      not target in Settings().ldap_channels:
      return "Nah, I don't like this channel that much"

    if not argument or argument == "":
      return "You have to specify the username or filter as argument"

    if '=' in argument:
      filt = argument.lower()
    else:
      filt = 'uid=' + argument.lower()
    con = ldap.initialize(Settings().ldap_url)
    try:
      sr = con.search_st(Settings().ldap_base, ldap.SCOPE_SUBTREE, \
          filt, timeout=1)
    except:
      return "LDAP failure, maybe you provided me with an invalid filter?"

    i=0
    for entry in sr:
      if not 'sn' in  entry[1]:
        continue

      i=i + 1
      if i == 6:
        bot.tell(network, target, ".. and " + str((len(sr) - i)) + \
            " more result(s)")
        return None

      name = entry[1]['sn'][0] + ", " + entry[1]['givenName'][0]
      uid = self._safe_get(entry, 'uid')
      email = self._safe_get(entry, 'gosaMailForwardingAddress')
      home =  self._safe_get(entry, 'homePhone')
      work =  self._safe_get(entry, 'telephoneNumber')
      name = name.decode('utf-8')

      txt = name.encode('utf-8') + " " + uid + " " + \
        (email if email else "") + " " + self._format_phone(home)
      if work:
        txt = txt + " (" + self._format_phone(work) + ")"

      bot.tell(network, target, txt)

    if i == 0:
      return "Couldn't find any matching users, sorry :("
    return None

if __name__ == "__main__":
  l = LdapcontactCommand()
  print l.trig_contact(None, None, "#dhtech", None, "")
  print l.trig_contact(None, None, "#dhtecasdh", None, "access")
  print l.trig_contact(None, None, "#dhtech", None, "access123")
  print l.trig_contact(None, None, "#dhtech", None, "bluecmd")
