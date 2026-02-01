FROM debian:stable-slim

ARG TARGET_USER=ansible

RUN apt-get update -q \
    && apt-get install -yq openssh-server sudo python3

RUN useradd -ms /bin/bash ${TARGET_USER} && \
    usermod -aG sudo ${TARGET_USER}

RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER root
COPY docker-entrypoint.sh /

ENV TARGET_USER=$TARGET_USER
CMD ["/docker-entrypoint.sh"]
