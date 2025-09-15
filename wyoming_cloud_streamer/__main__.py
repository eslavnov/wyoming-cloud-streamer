#!/usr/bin/env python3
import argparse
import asyncio
import json
import logging
from functools import partial
from pathlib import Path
from typing import Any, Dict, Set
import os

from wyoming.info import Attribution, Info, TtsProgram, TtsVoice, TtsVoiceSpeaker
from wyoming.server import AsyncServer

from . import __version__
from .handler import CloudStreamerEventHandler

_LOGGER = logging.getLogger(__name__)

async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", default="stdio://", help="unix:// or tcp://")
    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")
    parser.add_argument(
        "--log-format", default=logging.BASIC_FORMAT, help="Format for log messages"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Print version and exit",
    )
    
    parser.add_argument(
        "--streaming",
        action="store_true",
        help="Enable audio streaming on sentence boundaries",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO, format=args.log_format
    )
    _LOGGER.debug(args)


    with open("/app/wyoming_cloud_streamer/voices.json", "r", encoding="utf-8") as f:
        voices_data = json.load(f)

    voices = []
    for key in voices_data.keys():
        for voice in voices_data[key]["voices"]:
            for language in voices_data[key]["languages"]:
                voice_name = ""
                voice_description = ""
                if key == "google":
                    voice_name = language.replace('_', '-', 1)+"-Chirp3-HD-"+voice
                    voice_description = "google_"+voice
                    attribution=Attribution(
                            name="Google", url="https://cloud.google.com/text-to-speech/docs/chirp3-hd"
                        )
                elif key == "openai":
                    voice_name = language.replace('_', '-', 1)+"-openai-"+voice
                    voice_description = "openai_"+voice
                    attribution=Attribution(
                            name="OpenAI", url="https://platform.openai.com/docs/guides/text-to-speech"
                        )
                voices.append(
                    TtsVoice(
                        name=voice_name,
                        description=voice_description,
                        attribution=attribution,
                        installed=True,
                        version=None,
                        languages=[language],
                        speakers=None,
                    )
                )

    wyoming_info = Info(
        tts=[
            TtsProgram(
                name="Cloud TTS Streamer",
                description="Wyoming streaming proxy for cloud TTS providers",
                attribution=Attribution(
                    name="eslavnov", url="https://github.com/eslavnov/wyoming-cloud-streamer"
                ),
                installed=True,
                voices=sorted(voices, key=lambda v: v.name),
                version=__version__,
                supports_synthesize_streaming=True,
            )
        ],
    )

    # Start server 
    server = AsyncServer.from_uri(args.uri)

    _LOGGER.info("Ready")
    await server.run(
        partial(
            CloudStreamerEventHandler,
            wyoming_info,
            args,
            voices,
        )
    )

def run():
    asyncio.run(main())

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
