from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import socket
import serial
import pyvisa
from pathlib import Path

app = FastAPI(title="Balena Instrument Control Demo")

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class EthernetScpiRequest(BaseModel):
    host: str
    port: int = 5025
    command: str = "*IDN?"
    timeout_s: float = 3.0


class SerialRequest(BaseModel):
    port: str = "/dev/ttyUSB0"
    baudrate: int = 9600
    command: str = "*IDN?"
    timeout_s: float = 3.0


class VisaRequest(BaseModel):
    resource: str
    command: str = "*IDN?"


@app.get("/")
def index():
    return FileResponse(static_dir / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "instrument-control"}


@app.post("/api/ethernet-scpi/query")
def ethernet_scpi_query(req: EthernetScpiRequest):
    '''
    SCPI over raw TCP socket.
    Many instruments use port 5025 for SCPI over LAN.
    Example command: *IDN?
    '''
    try:
        with socket.create_connection((req.host, req.port), timeout=req.timeout_s) as sock:
            sock.settimeout(req.timeout_s)
            message = req.command.rstrip() + "\n"
            sock.sendall(message.encode("ascii"))
            data = sock.recv(4096)
            return {
                "transport": "ethernet_socket",
                "host": req.host,
                "port": req.port,
                "command": req.command,
                "response": data.decode(errors="replace").strip(),
            }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/serial/query")
def serial_query(req: SerialRequest):
    '''
    SCPI or text commands over serial / COM port.
    On Raspberry Pi this is usually /dev/ttyUSB0 or /dev/ttyACM0.
    On Windows this would be COM3, COM4, etc.
    '''
    try:
        with serial.Serial(req.port, req.baudrate, timeout=req.timeout_s) as ser:
            message = req.command.rstrip() + "\n"
            ser.write(message.encode("ascii"))
            ser.flush()
            data = ser.readline()
            return {
                "transport": "serial_com",
                "port": req.port,
                "baudrate": req.baudrate,
                "command": req.command,
                "response": data.decode(errors="replace").strip(),
            }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/visa/resources")
def visa_resources():
    '''
    Lists VISA resources visible from inside the container.
    pyvisa-py can discover some TCPIP/USB/serial instruments depending on drivers and permissions.
    '''
    try:
        rm = pyvisa.ResourceManager("@py")
        resources = rm.list_resources()
        return {"backend": "pyvisa-py", "resources": list(resources)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/visa/query")
def visa_query(req: VisaRequest):
    '''
    VISA abstraction layer.
    Example resources:
      TCPIP::192.168.1.50::5025::SOCKET
      ASRL/dev/ttyUSB0::INSTR
      USB0::0x1234::0x5678::SERIAL::INSTR
    '''
    try:
        rm = pyvisa.ResourceManager("@py")
        inst = rm.open_resource(req.resource)
        response = inst.query(req.command)
        inst.close()
        return {
            "transport": "visa",
            "resource": req.resource,
            "command": req.command,
            "response": response.strip(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/usb/devices")
def usb_devices_note():
    '''
    Minimal endpoint explaining USB access.
    For real USB listing, enter the container and run: lsusb
    '''
    return {
        "note": "USB devices need to be passed into the container or run with privileged=true.",
        "debug_command": "balena ssh <device> 'balena exec -it <container> lsusb'",
        "common_linux_devices": ["/dev/ttyUSB0", "/dev/ttyACM0", "/dev/usbtmc0"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
