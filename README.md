# MoonInTheMan — Balena Raspberry Pi Multi-Service Lab

Multi-container Raspberry Pi 4 project using Balena for embedded Linux, web dashboards, C/Node/Python demos, and CI.

---

## Current Services

### `python-flask` — Python / Flask / OpenCV
- USB webcam dashboard
- Live video + photo capture
- `/data` shared logging

**Browser:** `http://<PI-IP>:5000`

---

### `react-demo` — Node / Express / React
- Service hub dashboard
- Live clock + click counter
- Central service links
- `/data` logging

**Browser:** `http://<PI-IP>:3000`

---

### `express-demo` — Node / Express
- Beginner GET/POST demo
- Simple state control

**Browser:** `http://<PI-IP>:3001`

---

### `c-demo` — Raw C Socket Server + API
- HTML dashboard
- GET `/status`
- POST `/toggle` `/count` `/reset`
- `/data/c-demo.log`

**Browser:** `http://<PI-IP>:8080`

---

## Architecture

```text
BalenaOS
├── python-flask
├── react-demo
├── express-demo
└── c-demo
```

---

## Shared Volume

```text
/data
```

Examples:

```text
/data/python-flask.log
/data/react-demo.log
/data/c-demo.log
/data/photo.jpg
```

---

## Deploy

```bash
balena login
balena push timothy_reinhardt/moonintheman
```

---

## Debug

```bash
tail -f /data/python-flask.log
tail -f /data/react-demo.log
tail -f /data/c-demo.log
```

All:

```bash
tail -f /data/*.log
```

---

## GitHub CI

GitHub Actions automatically checks Docker builds on push:

```text
GitHub → Actions → Docker Build Check
```

Current CI:
- Python image build
- React image build
- Express image build
- C image build

---

## Useful Commands

```bash
ls /dev/video*
lsusb
ip addr
ls /data
```

---

## Fast Workflow

```bash
git add .
git commit -m "Update"
git push
balena push timothy_reinhardt/moonintheman
```
