FROM python:3.6
ENV PYTHONUNBUFFERED 1
MAINTAINER Jagjot Singh <jagjotsingh2008@gmail.com>
RUN MKDIR /app
WORKDIR /app
COPY . /app/
RUN pip install --no-cache-dir -r requirements.txt