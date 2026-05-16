# Balena Instrument Control Demo

A Raspberry Pi / Balena demo project for test-and-measurement style software.

It focuses on:

- Ethernet sockets
- COM / serial ports
- VISA
- SCPI
- USB-connected instruments

## Virtual Instrumentation Software Architecture 


```text
Browser UI
  ↓
FastAPI application logic
  ↓
Protocol layer
  ↓
Ethernet / Serial / VISA / USB
  ↓
SCPI-capable instrument
```
## Run locally

```bash
docker compose up --build
```

Open:

```text
http://localhost:8080
```


## Common SCPI command

```text
*IDN?
```

This asks the instrument to identify itself.

## Typical Ethernet SCPI

Many instruments use TCP port `5025`.

Example:

```text
Host: 192.168.1.50
Port: 5025
Command: *IDN?
```

## Typical Linux serial / COM ports

```text
/dev/ttyUSB0
/dev/ttyACM0
```

Windows equivalents would be:

```text
COM3
COM4
```

## Virtual Instrumentation Software Architecture examples

```text
TCPIP::192.168.1.50::5025::SOCKET
ASRL/dev/ttyUSB0::INSTR
USB0::0x1234::0x5678::SERIAL::INSTR
```



