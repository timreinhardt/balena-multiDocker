from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import socket
import serial
import pyvisa
from pathlib import Path
import logging
from datetime import datetime


# =========================================================
# FASTAPI APP SETUP
# =========================================================
app = FastAPI(title="Instrument Control Demo")

# Static web UI folder
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# =========================================================
# LOGGING 
# =========================================================
DATA_DIR = Path("/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = DATA_DIR / "instrument_control.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("instrument_control")


def log_event(event_type: str, message: str):
    """
    Unified logging helper.
    Keeps logs consistent and easy to grep/debug.
    """
    logger.info(f"{event_type} | {message}")


# Log service startup
log_event("STARTUP", "Instrument Control API service initialized")


# =========================================================
# REQUEST MODELS
# =========================================================
class EthernetScpiRequest(BaseModel):
    """
    SCPI over Ethernet (raw TCP socket).
    Typical LAN instruments use TCP port 5025.
    """
    host: str
    port: int = 5025
    command: str = "*IDN?"
    timeout_s: float = 3.0


class SerialRequest(BaseModel):
    """
    SCPI or text commands over serial.
    Linux examples:
      /dev/ttyUSB0
      /dev/ttyACM0
    Windows examples:
      COM3
      COM4
    """
    port: str = "/dev/ttyUSB0"
    baudrate: int = 9600
    command: str = "*IDN?"
    timeout_s: float = 3.0


class VisaRequest(BaseModel):
    """
    VISA abstraction layer request.
    VISA allows unified communication across USB, Ethernet, Serial, GPIB.
    """
    resource: str
    command: str = "*IDN?"


# =========================================================
# WEB UI ROUTES
# =========================================================
@app.get("/")
def index():
    """
    Serves the frontend HTML dashboard.
    """
    log_event("HTTP", "Frontend index page served")
    return FileResponse(static_dir / "index.html")


@app.get("/api/health")
def health():
    """
    Basic health endpoint for service monitoring.
    """
    log_event("HEALTH", "Health check OK")
    return {
        "status": "ok",
        "service": "instrument-control",
        "timestamp": datetime.utcnow().isoformat(),
    }


# =========================================================
# ETHERNET SCPI
# =========================================================
@app.post("/api/ethernet-scpi/query")
def ethernet_scpi_query(req: EthernetScpiRequest):
    """
    SCPI over raw TCP socket.
    Example:
      Host: 192.168.1.100
      Port: 5025
      Command: *IDN?
    """
    log_event(
        "ETHERNET_REQUEST",
        f"host={req.host}, port={req.port}, command={req.command}"
    )

    try:
        with socket.create_connection((req.host, req.port), timeout=req.timeout_s) as sock:
            sock.settimeout(req.timeout_s)

            # SCPI commands usually terminate with newline
            message = req.command.rstrip() + "\n"
            sock.sendall(message.encode("ascii"))

            data = sock.recv(4096)
            response = data.decode(errors="replace").strip()

            log_event(
                "ETHERNET_SUCCESS",
                f"host={req.host}, response={response}"
            )

            return {
                "transport": "ethernet_socket",
                "host": req.host,
                "port": req.port,
                "command": req.command,
                "response": response,
            }

    except Exception as exc:
        log_event("ETHERNET_ERROR", str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


# =========================================================
# SERIAL / COM
# =========================================================
@app.post("/api/serial/query")
def serial_query(req: SerialRequest):
    """
    Serial communication.
    Common for:
    - USB serial adapters
    - UART bridges
    - Legacy instruments
    """
    log_event(
        "SERIAL_REQUEST",
        f"port={req.port}, baud={req.baudrate}, command={req.command}"
    )

    try:
        with serial.Serial(req.port, req.baudrate, timeout=req.timeout_s) as ser:
            message = req.command.rstrip() + "\n"

            ser.write(message.encode("ascii"))
            ser.flush()

            data = ser.readline()
            response = data.decode(errors="replace").strip()

            log_event(
                "SERIAL_SUCCESS",
                f"port={req.port}, response={response}"
            )

            return {
                "transport": "serial_com",
                "port": req.port,
                "baudrate": req.baudrate,
                "command": req.command,
                "response": response,
            }

    except Exception as exc:
        log_event("SERIAL_ERROR", str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


# =========================================================
# Virtual Instrument Software Architecture RESOURCE LIST
# =========================================================
@app.get("/api/visa/resources")
def visa_resources():
    """
    Lists all VISA-visible instruments.
    pyvisa-py backend avoids requiring NI-VISA.
    """
    log_event("VISA_SCAN", "Scanning VISA resources")

    try:
        rm = pyvisa.ResourceManager("@py")
        resources = rm.list_resources()

        log_event(
            "VISA_SCAN_SUCCESS",
            f"resources_found={len(resources)}"
        )

        return {
            "backend": "pyvisa-py",
            "resources": list(resources),
        }

    except Exception as exc:
        log_event("VISA_SCAN_ERROR", str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


# =========================================================
# VISA QUERY
# =========================================================
@app.post("/api/visa/query")
def visa_query(req: VisaRequest):
    """
    VISA examples:
      TCPIP::192.168.1.50::5025::SOCKET
      ASRL/dev/ttyUSB0::INSTR
      USB0::0x1234::0x5678::SERIAL::INSTR
    """
    log_event(
        "VISA_REQUEST",
        f"resource={req.resource}, command={req.command}"
    )

    try:
        rm = pyvisa.ResourceManager("@py")
        inst = rm.open_resource(req.resource)

        response = inst.query(req.command).strip()

        inst.close()

        log_event(
            "VISA_SUCCESS",
            f"resource={req.resource}, response={response}"
        )

        return {
            "transport": "visa",
            "resource": req.resource,
            "command": req.command,
            "response": response,
        }

    except Exception as exc:
        log_event("VISA_ERROR", str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


# =========================================================
# USB INFO
# =========================================================
@app.get("/api/usb/devices")
def usb_devices_note():
    """
    USB devices often need:
    - privileged mode
    - device mapping
    - proper Linux permissions
    """
    log_event("USB_INFO", "USB guidance endpoint called")

    return {
        "note": "USB devices need container permissions or privileged=true.",
        "debug_command": "balena ssh <device> 'balena exec -it <container> lsusb'",
        "common_linux_devices": [
            "/dev/ttyUSB0",
            "/dev/ttyACM0",
            "/dev/usbtmc0"
        ],
    }


# =========================================================
# MAIN ENTRY
# =========================================================
if __name__ == "__main__":
    import uvicorn

    log_event("STARTUP", "Launching Uvicorn server on 0.0.0.0:8080")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080
    )