FROM python:2-alpine

ADD / /pyirkbot/

CMD ["python", "-u", "/pyirkbot/main.py"]
