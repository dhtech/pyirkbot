FROM debian:testing

RUN apt-get update; \
  DEBIAN_FRONTEND=noninteractive apt-get install -y dumb-init python python-svn python-simplejson python-ldap

ADD / /pyirkbot/

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python2", "-u", "/pyirkbot/main.py"]
