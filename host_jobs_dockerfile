FROM alpine:latest

RUN apk add --update \
    py3-pip \
    python3

COPY promote_me_not /promote_me_not
COPY requirements.txt /promote_me_not
WORKDIR /promote_me_not

RUN pip3 install -r requirements.txt

EXPOSE 8001
cmd ["python3","manage.py","runserver", "0.0.0.0:8001"]
