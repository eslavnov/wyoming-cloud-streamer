# Wyoming Cloud Streamer

[Wyoming protocol](https://github.com/rhasspy/wyoming) server for cloud TTS engines (for now, it supports only Google Cloud and OpenAI).

Ask ChatGPT to tell you a long story, and you will hear the response audio almost immediately instead of waiting for the whole pipeline to finish.

Works with Home Assistant Voice Preview Edition (HAVPE) devices. 

This project builds on [wyoming-piper](https://github.com/rhasspy/wyoming-piper) by Michael Hansen, licensed under MIT.


## Getting started

1. Add the repository and install Wyoming Cloud Streamer from the Add-on store:

    [![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Feslavnov%2Fwyoming-cloud-streamer)

1. Configure Wyoming Cloud Streamer addon settings:
    1. To use Google Cloud TTS, you need a service account json from Google Cloud. Follow [these instructions](https://www.home-assistant.io/integrations/google_cloud/#obtaining-service-account-file), you need only text-to-speech. Set the correct path in the addon settings (the default is `/config/SERVICE_ACCOUNT.json`)
    2. To use OpenAI, you need an API key, [get it here](https://platform.openai.com/settings/organization/api-keys)

1. Configure Wyoming Protocol in Home Assistant:
    1. Go to Settings => Integrations => Add Integration => Wyoming Protocol
    2. Add ip/hostname (you can use `127.0.0.1`) and port (the default one is `10200`)

1. Add Wyoming Cloud Streamer to Voice assistants:
    1. Go to Settings => Voice assistants => choose your assistant => Text-to-speech => Cloud TTS Streamer
    2. Select the desired voice and language, and you are good to go!
