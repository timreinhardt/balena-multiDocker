import socket
import time
import math
import random

HOST = "0.0.0.0"
PORT = 5025

CENTER_FREQ_HZ = 2_400_000_000
SPAN_HZ = 100_000_000


def log(message):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)


def fake_trace_data():
    values = []

    for i in range(51):
        # Fake RF-looking trace around -50 dBm with a peak near centre
        x = (i - 25) / 25
        peak = 25 * math.exp(-12 * x * x)
        noise = random.uniform(-1.5, 1.5)
        power_dbm = -70 + peak + noise
        values.append(f"{power_dbm:.2f}")

    return ",".join(values)


def handle_command(command):
    cmd = command.strip().upper()

    if cmd == "*IDN?":
        return "YIC,MOCK-SPECTRUM-ANALYZER,MOCK12345,1.0"

    if cmd == ":MEAS:VOLT?":
        return "3.300"

    if cmd == ":MEAS:CURR?":
        return "0.125"

    if cmd == ":FREQ:CENT?":
        return str(CENTER_FREQ_HZ)

    if cmd.startswith(":FREQ:CENT "):
        return "OK"

    if cmd == ":FREQ:SPAN?":
        return str(SPAN_HZ)

    if cmd.startswith(":FREQ:SPAN "):
        return "OK"

    if cmd == ":INIT":
        return "OK"

    if cmd == ":TRAC:DATA?":
        return fake_trace_data()

    if cmd == ":SYST:ERR?":
        return "0,No error"

    return f"-113,Undefined header: {command}"


def main():
    log(f"SCPI simulator listening on {HOST}:{PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)

        while True:
            conn, addr = server.accept()
            log(f"Client connected: {addr}")

            with conn:
                while True:
                    data = conn.recv(1024)

                    if not data:
                        log(f"Client disconnected: {addr}")
                        break

                    command = data.decode(errors="replace").strip()
                    log(f"RX: {command}")

                    response = handle_command(command)
                    log(f"TX: {response}")

                    conn.sendall((response + "\n").encode())


if __name__ == "__main__":
    main()