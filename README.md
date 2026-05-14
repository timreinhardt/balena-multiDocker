# MoonInTheMan Balena Raspberry Pi Multi-Service Dashboard

## What this project does

Runs a **multi-service Balena deployment** on a Raspberry Pi 4.

This project currently includes:

------------------------------------------------------------------------

# Service 1: `python-flask`

## Python + Flask + OpenCV webcam dashboard

### Features:

-   Browser dashboard
-   Detect USB webcam
-   Start / Stop live camera
-   Live video stream
-   Take photo
-   Display latest saved photo
-   Persistent shared logging via `/data`
-   Shared photo storage

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

-   React frontend demo
-   Live browser clock
-   Click counter
-   Demonstrates JavaScript / React deployment
-   Links to Python webcam dashboard
-   Persistent shared logging via `/data`

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

# How to debug quickly

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

# Versioning

### Current:

``` text
v1.3-dual-service
```

### Suggested:

``` text
v1.4-shared-volume
v1.5-camera-fix
```

------------------------------------------------------------------------

# Interview Talking Point

> Multi-container Raspberry Pi deployment using Balena:
> Python/Flask/OpenCV backend + React frontend, isolated by service,
> sharing one Linux kernel and a persistent shared Docker volume.

------------------------------------------------------------------------

# Fast Workflow

## Edit Python:

``` bash
nano app.py
```

## Edit React:

``` bash
nano react-demo/server.js
```

## Edit Compose:

``` bash
nano docker-compose.yml
```

## Push:

``` bash
balena push timothy_reinhardt/moonintheman
```

## Debug:

``` bash
tail -f /data/python-flask.log /data/react-demo.log
```
