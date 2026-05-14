# MoonInTheMan Balena Raspberry Pi Multi-Service Dashboard

## What this project does

Runs a **multi-service Balena deployment** on a Raspberry Pi 4.

This project currently includes:

------------------------------------------------------------------------

# Service 1: `python-flask`

## Python + Flask + OpenCV webcam dashboard

### Features:

- Browser dashboard
- USB webcam detection
- Live video + camera control
- Photo capture + latest image
- Shared `/data` logging + storage

### Browser:

``` text
http://<PI-IP>:5000
```

### Example:

``` text
http://192.168.1.47:5000
```

------------------------------------------------------------------------

# Service 2: `react-demo`

## Node + Express + React dashboard

### Features:

- React dashboard demo
- Live clock + click counter
- Python dashboard link
- Shared `/data` logging

### Browser:

``` text
http://<PI-IP>:3000
```

### Example:

``` text
http://192.168.1.47:3000
```

------------------------------------------------------------------------

# Architecture

``` text
Raspberry Pi 4
│
├── Host OS (BalenaOS)
│
├── python-flask
│   └── Python / Flask / OpenCV
│
└── react-demo
    └── Node / Express / React
```

------------------------------------------------------------------------

# Shared Persistent Volume

Both services mount:

``` text
/data
```

### Shared files:

``` text
/data/python-flask.log
/data/react-demo.log
/data/photo.jpg
```

------------------------------------------------------------------------

# Folder Structure

``` text
balena-hello/
│
├── Dockerfile
├── docker-compose.yml
├── app.py
├── README.md
│
└── react-demo/
    ├── Dockerfile
    ├── package.json
    └── server.js
```

------------------------------------------------------------------------

# Docker Images

## Root Dockerfile:

``` dockerfile
FROM balenalib/raspberrypi4-64-python:3.11
```

### Purpose:

Python webcam + Flask backend

------------------------------------------------------------------------

## React Dockerfile:

``` dockerfile
FROM balenalib/raspberrypi4-64-node:20
```

### Purpose:

React frontend demo

------------------------------------------------------------------------

# Docker Compose

``` yaml
version: "2.1"

services:
  python-flask:
    build: .
    privileged: true
    ports:
      - "5000:5000"
    volumes:
      - shared-data:/data

  react-demo:
    build: ./react-demo
    ports:
      - "3000:3000"
    volumes:
      - shared-data:/data

volumes:
  shared-data:
```

------------------------------------------------------------------------

# How to deploy

From this folder on Mac:

``` bash
cd ~/balena-hello
balena push timothy_reinhardt/moonintheman
```

------------------------------------------------------------------------

# How to debug 

## Python Flask logs:

``` bash
tail -f /data/python-flask.log
```

## React Demo logs:

``` bash
tail -f /data/react-demo.log
```

## Tail BOTH:

``` bash
tail -f /data/python-flask.log /data/react-demo.log
```

------------------------------------------------------------------------

# Useful Host OS commands

## Check camera devices:

``` bash
ls /dev/video*
```

## Check USB devices:

``` bash
lsusb
```

## Check IP:

``` bash
ip addr
```

## Verify shared storage:

``` bash
ls /data
```

------------------------------------------------------------------------



# Fast Workflow

``` bash
balena login
```
## edit


## Push:

``` bash
balena push timothy_reinhardt/moonintheman
```

