FROM python:alpine

ADD / /pyirkbot/

CMD ["python", "-u", "/pyirkbot/main.py"]
