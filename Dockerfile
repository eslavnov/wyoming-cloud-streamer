ARG BUILD_ARCH
FROM ghcr.io/home-assistant/${BUILD_ARCH}-base-python:3.12-alpine3.20

# Small runtime tools used by the run script
RUN apk add --no-cache bash jq curl

# Bring in code + add-on files
WORKDIR /app
COPY . /app

# Install code and deps
RUN pip install --no-cache-dir . \
 && pip install --no-cache-dir google-cloud-texttospeech

# s6 service (provides /etc/services.d/wyoming/run)
COPY rootfs/ /
RUN sed -i 's/\r$//' /etc/services.d/wyoming/run && chmod +x /etc/services.d/wyoming/run

ENV PYTHONUNBUFFERED=1
