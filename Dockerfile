FROM python:2-stretch

RUN apt-get update; \
  DEBIAN_FRONTEND=noninteractive apt-get install -y dumb-init python-svn

ADD / /pyirkbot/

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python2", "-u", "/pyirkbot/main.py"]
