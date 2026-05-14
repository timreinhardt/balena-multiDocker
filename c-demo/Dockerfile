FROM balenalib/raspberrypi4-64-debian:bookworm

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY Makefile .
COPY main.c .

RUN make

CMD ["./c-demo"]