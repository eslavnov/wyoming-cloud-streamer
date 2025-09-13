# Hardcode a HA Python base so pip is present and s6 overlay is available
FROM ghcr.io/home-assistant/amd64-base-python:3.12-alpine3.20

# Small runtime tools used by the run script
RUN apk add --no-cache bash jq curl

# Bring in your code + add-on files
WORKDIR /app
COPY . /app

# Install your code and deps
# If you don't have pyproject.toml/setup.py, comment "pip install ." and just install deps.
RUN pip install --no-cache-dir . \
 && pip install --no-cache-dir google-cloud-texttospeech

# s6 service (provides /etc/services.d/wyoming/run)
COPY rootfs/ /

ENV PYTHONUNBUFFERED=1
