FROM balenalib/raspberrypi4-64-python:3.11

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    v4l-utils \
    libglib2.0-0 \
    libgl1 \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask opencv-python-headless

COPY app.py .

CMD ["python3", "app.py"]