FROM python:3.8-slim
RUN apt-get update
RUN apt-get -y upgrade
# RUN apt-get -y install python3 python3-dev
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
