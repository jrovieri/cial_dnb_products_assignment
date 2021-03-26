FROM python:3

LABEL maintainer="jrovieri@gmail.com"

ADD main.py /usr/src/app/main.py
ADD requirements.txt /usr/src/app/requirements.txt
WORKDIR /usr/src/app

RUN sed -n '/pkg-resources==0.0.0/!p' requirements.txt > temp && mv temp requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT [ "python", "main.py" ]