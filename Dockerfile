FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    openssh-client \
    curl \
    git \
    netcat-openbsd \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir ansible pyyaml paramiko

RUN ansible-galaxy collection install cisco.ios cisco.nxos arista.eos

WORKDIR /app
COPY . .

EXPOSE 3000
CMD ["python3", "server.py"]