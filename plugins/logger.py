# coding: utf-8
# Author: Christian Svensson <blue@cmd.nu>

# Note: first %s = team, second %s = time via log_svn_time_format
# def _get_svn_url(settings, svn):
#   event = svn.cat ("https://cmd.nu/svn/trunk/test").strip()
#   return "https://cmd.nu/svn/trunk/" + event + "%s_%s.txt"
#
# log_svn_url = _get_svn_url
# log_svn_channels = [ '#mychannel' ]
# log_svn_username = "user"
# log_svn_password = "password"
# log_svn_time_format = "%Y%m%d"
# log_svn_teams = [ "access", "team" ]

import collections
import grp
import os
import pysvn
from tempfile import NamedTemporaryFile
from datetime import datetime
from commands import Command
from settings import Settings

class Logger(Command):
  hooks = [ "on_privmsg" ]
  def __init__(self):
    self.logs = {}

  def on_load(self):
    pass

  def on_unload(self):
    pass

  def on_privmsg(self, bot, source, target, message, network, **kwargs):
    if not target in self.logs:
      return None

    # Log it!
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    source = source.split('!')[0]
    self.logs[target]["log"].append("%s %s> %s" % (
      time, source.rjust(16), message))
    self.logs[target]["participants"][source] += 1
    return None

  def trig_logstart(self, bot, source, target, trigger, argument):
    if Settings().log_svn_channels != None and \
      not target in Settings().log_svn_channels:
      return "Nah, I don't like this channel that much"

    if target in self.logs:
      return "I'm already logging this channel"

    if not argument or argument == "":
      return "You have to specify the group name as argument"

    team = argument.lower()

    if not team in Settings().log_svn_teams:
      return "Nobody told me there is a '" + team + "' group :("

    time = datetime.now().strftime(Settings().log_svn_time_format)

    self.logs[target] = { "team" : team, "time": time, "log": [],
        "participants": collections.defaultdict(int)}
    return "Logging ..."

  def trig_logstop(self, bot, source, target, trigger, argument):
    if not target in self.logs:
      return "Sorry, nobody told me to record this channel :("

    log = self.logs[target]
    report = []
    report.append("=== Report ===")

    if log["team"] == "team":
      group_name = "tech-%s" % (Settings().event(), )
    else:
      group_name = "%s-%s" % (log["team"], Settings().event())
    missing_members = set()
    group = None
    try:
      group = grp.getgrnam(group_name)
      missing_members = set(group[3])
    except KeyError:
      report.append(
          "(Group named '%s' does not exsist, cannot list non-attendees)" % (
            group_name, ))

    report.append("- Participants:")
    participants = sorted(log["participants"])
    report.extend(participants)
    missing_members -= set(participants)

    if group:
      report.append("- Non-attendees:")
      report.extend(missing_members)

    tmp = NamedTemporaryFile(delete=False)
    tmp.write("\n".join(log["log"]))
    tmp.write("\n");
    tmp.write("\n".join(report));
    tmp.write("\n");
    tmp.close()

    url = Settings().log_svn_url() % (log["team"], log["time"])
    try:
      Settings().svn().import_ (tmp.name, url,
          'IRC auto logger: ' + log["team"] + ' @ ' + log["time"])

      os.unlink(tmp.name)
    except pysvn._pysvn.ClientError as e:
      return "Oops! I failed to upload the log (" + tmp.name + \
        "), error is: " + str(e)

    del self.logs[target]
    return "Log uploaded to " + url

if __name__ == "__main__":
  l = Logger()
  print l.trig_logstart(None, None, "#dhtech", None, "")
  print l.trig_logstart(None, None, "#dhtecasdh", None, "access")
  print l.trig_logstart(None, None, "#dhtech", None, "access123")
  print l.trig_logstart(None, None, "#dhtech", None, "access")
  print l.trig_logstart(None, None, "#dhtech", None, "access")
  print l.on_privmsg(None, "blueCmd", "#dhtech", "Tja lol", None)
  print l.on_privmsg(None, "soundguuf", "#dhtech", "Hej hej hej hej", None)
  print l.trig_logstop(None, None, "#dhtech", None, "")
  print l.trig_logstop(None, None, "#dhtech", None, "")
  print l.trig_logstart(None, None, "#dhtech", None, "access")
  print l.on_privmsg(None, "blueCmd", "#dhtech", "Tja lol", None)
  print l.on_privmsg(None, "blueCmd", "#dhtech", "Tja lol", None)
  print l.on_privmsg(None, "soundguuf", "#dhtech", "Hej hej hej hej", None)
  print l.trig_logstop(None, None, "#dhtech", None, "")
