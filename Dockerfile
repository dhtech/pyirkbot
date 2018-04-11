FROM python:alpine

ADD / /pyirkbot/

RUN ["python" "-u" "/pyirkbot/main.py"]
