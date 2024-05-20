FROM python:3.11-slim

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y install git

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

COPY ./docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# CMD ["sh", "/docker/entrypoint.sh"]
