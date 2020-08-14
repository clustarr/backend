FROM python:3.8-alpine

WORKDIR /usr/src/app

RUN set -x \
    # requirements for cryptography (installed by ansible)
    && apk add --no-cache build-base libressl-dev musl-dev libffi-dev \
    # requirements for ansible
    && apk add --no-cache openssh-client sshpass

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
