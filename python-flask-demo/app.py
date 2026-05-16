from flask import Flask, Response, redirect, url_for
import cv2
import os
import time
import socket
import traceback

app = Flask(__name__)

camera_on = False
camera = None

APP_VERSION = "v1.1-logging"
LOG_DIR = "/data"
LOG_FILE = f"{LOG_DIR}/python-flask.log"
PHOTO_PATH = f"{LOG_DIR}/photo.jpg"

os.makedirs(LOG_DIR, exist_ok=True)

def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message, flush=True)

    try:
        with open(LOG_FILE, "a") as f:
            f.write(full_message + "\n")
    except Exception as e:
        print(f"LOG FILE WRITE FAILED: {e}", flush=True)


def log_error(context, error):
    log(f"ERROR in {context}: {error}")
    log(traceback.format_exc())


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "PI-IP-UNKNOWN"
    finally:
        s.close()


def find_camera():
    for dev in ["/dev/video0", "/dev/video1", "/dev/video2", "/dev/video19"]:
        if os.path.exists(dev):
            return dev
    return None


def start_camera():
    global camera, camera_on

    try:
        dev = find_camera()
        if not dev:
            log("No camera found")
            return False

        if camera is None:
            log(f"Opening camera: {dev}")
            camera = cv2.VideoCapture(dev, cv2.CAP_V4L2)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        opened = camera.isOpened()
        log(f"Camera opened status: {opened}")

        camera_on = opened
        return opened

    except Exception as e:
        log_error("start_camera", e)
        return False


def stop_camera():
    global camera, camera_on

    try:
        camera_on = False

        if camera is not None:
            log("Releasing camera")
            camera.release()
            camera = None

    except Exception as e:
        log_error("stop_camera", e)


def generate_frames():
    global camera

    while camera_on:
        try:
            if camera is None:
                log("generate_frames stopped: camera is None")
                break

            success, frame = camera.read()

            if not success or frame is None:
                log("Failed to read frame")
                time.sleep(0.5)
                continue

            ret, buffer = cv2.imencode(".jpg", frame)

            if not ret:
                log("Failed to encode frame")
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                buffer.tobytes() +
                b"\r\n"
            )

        except Exception as e:
            log_error("generate_frames", e)
            time.sleep(1)


@app.route("/")
def index():
    video_html = ""

    if camera_on:
        video_html = '<h2>Live Video</h2><img src="/video_feed" width="640">'

    photo_html = ""
    if os.path.exists(PHOTO_PATH):
        photo_html = f'<h2>Last Photo</h2><img src="/photo.jpg?{time.time()}" width="640">'

    return f"""
    <html>
    <head>
        <title>Pi Live Webcam Dashboard {APP_VERSION}</title>
        <style>
            body {{ font-family: Arial; background: #111; color: #00ff66; padding: 25px; }}
            h1 {{ color: #00ccff; }}
            button {{ font-size: 22px; padding: 12px; margin: 8px; }}
            .box {{ border: 1px solid #00ff66; padding: 15px; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <h1>Pi Live USB Webcam Dashboard</h1>

        <div class="box">
            <p>Release: <b>{APP_VERSION}</b></p>
            <p>Server Time: <b>{time.strftime("%Y-%m-%d %H:%M:%S")}</b></p>
            <p>Camera state: <b>{"ON" if camera_on else "OFF"}</b></p>
            <p>Detected device: <b>{find_camera()}</b></p>
            <p>Open at: <b>http://{get_local_ip()}:5000</b></p>
            <p>Log file: <b>{LOG_FILE}</b></p>
        </div>

        <form action="/on" method="post"><button>Start Live Video</button></form>
        <form action="/off" method="post"><button>Stop Camera</button></form>
        <form action="/take_photo" method="post"><button>Take Photo</button></form>

        <hr>
        {video_html}
        {photo_html}
    </body>
    </html>
    """


@app.route("/video_feed")
def video_feed():
    log("Video feed requested")
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/on", methods=["POST"])
def on():
    log("Start Live Video clicked")
    start_camera()
    return redirect(url_for("index"))


@app.route("/off", methods=["POST"])
def off():
    log("Stop Camera clicked")
    stop_camera()
    return redirect(url_for("index"))


@app.route("/take_photo", methods=["POST"])
def take_photo_route():
    global camera

    log("Take Photo clicked")

    try:
        if camera is None:
            start_camera()

        if camera is not None:
            success, frame = camera.read()
            log(f"Photo capture success: {success}")

            if success and frame is not None:
                log(f"Frame shape: {frame.shape}")
                saved = cv2.imwrite(PHOTO_PATH, frame)
                log(f"Photo saved status: {saved} path={PHOTO_PATH}")
            else:
                log("Failed to take photo: no valid frame")

    except Exception as e:
        log_error("take_photo_route", e)

    return redirect(url_for("index"))


@app.route("/photo.jpg")
def photo_image():
    exists = os.path.exists(PHOTO_PATH)
    log(f"Serving photo request. Exists={exists} path={PHOTO_PATH}")

    if exists:
        return open(PHOTO_PATH, "rb").read(), 200, {"Content-Type": "image/jpeg"}

    return "No photo yet", 404


local_ip = get_local_ip()

log("========================================")
log(f"Starting Pi Live Webcam Dashboard | {APP_VERSION}")
log(f"Detected camera device: {find_camera()}")
log(f"Open browser at: http://{local_ip}:5000")
log(f"Writing local logs to: {LOG_FILE}")
log("========================================")

app.run(host="0.0.0.0", port=5000, threaded=True)