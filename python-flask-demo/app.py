from flask import Flask, Response, redirect, url_for, jsonify
import cv2
import os
import time
import socket
import traceback


# ---------------------------------------------------------
# Flask app setup
# ---------------------------------------------------------
app = Flask(__name__)

# Global camera state
camera_on = False
camera = None

# App/version/logging paths
APP_VERSION = "v1.2-live-log-panel"
LOG_DIR = "/data"
LOG_FILE = f"{LOG_DIR}/python-flask.log"
PHOTO_PATH = f"{LOG_DIR}/photo.jpg"

# Ensure persistent data/log folder exists
os.makedirs(LOG_DIR, exist_ok=True)


# ---------------------------------------------------------
# Logging helper
# Logs to both Docker console and persistent file
# ---------------------------------------------------------
def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"

    print(full_message, flush=True)

    try:
        with open(LOG_FILE, "a") as f:
            f.write(full_message + "\n")
    except Exception as e:
        print(f"LOG FILE WRITE FAILED: {e}", flush=True)


# ---------------------------------------------------------
# API route used by browser JavaScript to read latest log tail
# ---------------------------------------------------------
@app.route("/logs")
def get_logs():
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()

        return jsonify({
            "logs": "".join(lines[-50:])
        })

    except Exception as e:
        return jsonify({
            "logs": f"Log read error: {str(e)}"
        })


# ---------------------------------------------------------
# Error logger helper
# Includes stack trace
# ---------------------------------------------------------
def log_error(context, error):
    log(f"ERROR in {context}: {error}")
    log(traceback.format_exc())


# ---------------------------------------------------------
# Get container/local IP address
# Note: this is often Docker internal IP, not always browser URL
# ---------------------------------------------------------
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "PI-IP-UNKNOWN"
    finally:
        s.close()


# ---------------------------------------------------------
# Find likely Linux video device
# USB webcams usually appear as /dev/video0
# ---------------------------------------------------------
def find_camera():
    for dev in ["/dev/video0", "/dev/video1", "/dev/video2", "/dev/video19"]:
        if os.path.exists(dev):
            return dev
    return None


# ---------------------------------------------------------
# Start/open camera
# ---------------------------------------------------------
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

            # Set requested camera resolution
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        opened = camera.isOpened()
        log(f"Camera opened status: {opened}")

        camera_on = opened
        return opened

    except Exception as e:
        log_error("start_camera", e)
        return False


# ---------------------------------------------------------
# Stop/release camera
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# Frame generator for MJPEG live video stream
# Browser receives a continuous stream of JPEG frames
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# Main dashboard page
# Left column: system/camera details
# Right column: live tail of /data/python-flask.log
# ---------------------------------------------------------
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
            body {{
                font-family: Arial;
                background: #111;
                color: #00ff66;
                padding: 25px;
            }}

            h1 {{
                color: #00ccff;
            }}

            button {{
                font-size: 22px;
                padding: 12px;
                margin: 8px;
            }}

            .box {{
                border: 1px solid #00ff66;
                padding: 15px;
                margin-top: 15px;
                display: grid;
                grid-template-columns: 1fr 1.5fr;
                gap: 20px;
                align-items: start;
            }}

            #logOutput {{
                background: black;
                color: #00ff66;
                padding: 10px;
                height: 220px;
                overflow-y: scroll;
                border: 1px solid #00ff66;
                white-space: pre-wrap;
                font-size: 13px;
            }}
        </style>
    </head>

    <body>
        <h1>Pi Live USB Webcam Dashboard</h1>

        <div class="box">
            <div>
                <p>Release: <b>{APP_VERSION}</b></p>
                <p>Server Time: <b>{time.strftime("%Y-%m-%d %H:%M:%S")}</b></p>
                <p>Camera state: <b>{"ON" if camera_on else "OFF"}</b></p>
                <p>Detected device: <b>{find_camera()}</b></p>
                <p>Open at: <b>http://{get_local_ip()}:5000</b></p>
                <p>Log file: <b>{LOG_FILE}</b></p>
            </div>

            <div>
                <h3>Live Log Tail</h3>
                <pre id="logOutput">Loading logs...</pre>
            </div>
        </div>

        <form action="/on" method="post">
            <button>Start Live Video</button>
        </form>

        <form action="/off" method="post">
            <button>Stop Camera</button>
        </form>

        <form action="/take_photo" method="post">
            <button>Take Photo</button>
        </form>

        <hr>

        {video_html}
        {photo_html}

        <script>
            // Poll Flask /logs endpoint every 2 seconds
            async function updateLogs() {{
                try {{
                    const response = await fetch('/logs');
                    const data = await response.json();

                    const logBox = document.getElementById("logOutput");
                    logBox.textContent = data.logs;

                    // Keep log view scrolled to newest line
                    logBox.scrollTop = logBox.scrollHeight;
                }} catch (err) {{
                    console.error("Log fetch failed:", err);
                }}
            }}

            setInterval(updateLogs, 2000);
            updateLogs();
        </script>
    </body>
    </html>
    """


# ---------------------------------------------------------
# MJPEG video stream route
# ---------------------------------------------------------
@app.route("/video_feed")
def video_feed():
    log("Video feed requested")

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ---------------------------------------------------------
# Start camera button route
# ---------------------------------------------------------
@app.route("/on", methods=["POST"])
def on():
    log("Start Live Video clicked")
    start_camera()
    return redirect(url_for("index"))


# ---------------------------------------------------------
# Stop camera button route
# ---------------------------------------------------------
@app.route("/off", methods=["POST"])
def off():
    log("Stop Camera clicked")
    stop_camera()
    return redirect(url_for("index"))


# ---------------------------------------------------------
# Take still photo route
# Saves latest frame to /data/photo.jpg
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# Serve saved photo
# ---------------------------------------------------------
@app.route("/photo.jpg")
def photo_image():
    exists = os.path.exists(PHOTO_PATH)
    log(f"Serving photo request. Exists={exists} path={PHOTO_PATH}")

    if exists:
        return open(PHOTO_PATH, "rb").read(), 200, {"Content-Type": "image/jpeg"}

    return "No photo yet", 404


# ---------------------------------------------------------
# App startup logging
# ---------------------------------------------------------
local_ip = get_local_ip()

log("========================================")
log(f"Starting Pi Live Webcam Dashboard | {APP_VERSION}")
log(f"Detected camera device: {find_camera()}")
log(f"Open browser at: http://{local_ip}:5000")
log(f"Writing local logs to: {LOG_FILE}")
log("========================================")


# ---------------------------------------------------------
# Start Flask server
# threaded=True allows video stream and log polling together
# ---------------------------------------------------------
app.run(host="0.0.0.0", port=5000, threaded=True)