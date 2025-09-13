# Wyoming Cloud Streamer

[Wyoming protocol](https://github.com/rhasspy/wyoming) server for cloud TTS engines.

This project builds on [wyoming-piper](https://github.com/rhasspy/wyoming-piper) by Michael Hansen, licensed under MIT.

## Home Assistant Add-on

[![Show add-on](https://my.home-assistant.io/badges/supervisor_addon.svg)](https://my.home-assistant.io/redirect/supervisor_addon/?addon=core_piper)

[Source](https://github.com/home-assistant/addons/tree/master/piper)

## Getting started

1. Install the add-on:

    ``` sh
    git clone https://github.com/rhasspy/wyoming-piper.git
    cd wyoming-piper
    script/setup
    ```

1. Configure Wyoming Cloud Streamer addon settings:
    ```
    GCP credentials for Google Cloud TTS
    Open AI API key for openAI TTS
    The rest can be left as defaults
    ```

1. Configure Wyoming Protocol in HASS
    ```
    Settings => Integrations => Add Integration => Wyoming Protocol
    Add ip/hostname and port (default is 10200)
    ```

1. Add Wyoming Cloud Streamer to Voice Assistant in HASS
    ```
    Settings => Voice Assistant => select your assitant => Text-to-speech => Wyoming Cloud Streamer
    Select the desired voice and language settings and you are good to go!
    ```
