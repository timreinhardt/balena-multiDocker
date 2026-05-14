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
-   Local persistent logging

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
-   Local persistent logging

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
tail -f /mnt/data/python-flask.log
```

## React Demo logs:

``` bash
tail -f /mnt/data/react-demo.log
```

## Tail BOTH:

``` bash
tail -f /mnt/data/python-flask.log /mnt/data/react-demo.log
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

------------------------------------------------------------------------

# Versioning

### Current:

``` text
v1.1-live-ip
```

### Suggested:

``` text
v1.2-local-logging
v1.3-react-demo
```
