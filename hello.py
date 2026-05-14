import time

while True:
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp_c = int(f.read().strip()) / 1000
        print(f"Hello Timothy — Pi is alive | CPU temp={temp_c:.1f}C")
    except Exception as e:
        print(f"Hello Timothy — Pi is alive | temp read failed: {e}")

    time.sleep(3)
