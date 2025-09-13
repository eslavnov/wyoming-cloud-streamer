"""Event handler for clients of the server (multi-engine)."""

import argparse
import asyncio
import logging
from typing import Any, Dict, Optional

from sentence_stream import SentenceBoundaryDetector
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.error import Error
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler
from wyoming.tts import (
    Synthesize,
    SynthesizeChunk,
    SynthesizeStart,
    SynthesizeStop,
    SynthesizeStopped,
)

from .engines import ENGINE_REGISTRY, AudioFormat

_LOGGER = logging.getLogger(__name__)


class CloudStreamerEventHandler(AsyncEventHandler):
    def __init__(
        self,
        wyoming_info: Info,
        cli_args: argparse.Namespace,
        voices_info: Dict[str, Any],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.cli_args = cli_args
        self.wyoming_info_event = wyoming_info.event()
        self.voices_info = voices_info

        self.is_streaming: Optional[bool] = None
        self.sbd = SentenceBoundaryDetector()
        self._synthesize: Optional[Synthesize] = None

    # ------------------------------- Event loop -------------------------------

    async def handle_event(self, event: Event) -> bool:
        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        try:
            # One-shot synth (no Wyoming streaming)
            if Synthesize.is_type(event.type) and not self.is_streaming:
                synthesize = Synthesize.from_event(event)

                # Collapse lines
                text = " ".join(synthesize.text.strip().splitlines())
                if not text:
                    await self.write_event(AudioStop().event())
                    return True

                voice_name = (
                    (synthesize.voice.name if synthesize.voice else None)
                    or getattr(self.cli_args, "voice", "en-US-Chirp3-HD-Charon")
                )

                await self._synthesize_with_engine(text, voice_name)
                return True

            # Streaming disabled at CLI level?
            if not getattr(self.cli_args, "streaming", True):
                return True

            # Stream start
            if SynthesizeStart.is_type(event.type):
                stream_start = SynthesizeStart.from_event(event)
                self.is_streaming = True
                self.sbd = SentenceBoundaryDetector()
                self._synthesize = Synthesize(text="", voice=stream_start.voice)
                _LOGGER.debug("Text stream started: voice=%s", stream_start.voice)
                return True

            # Stream chunk
            if SynthesizeChunk.is_type(event.type):
                assert self._synthesize is not None
                stream_chunk = SynthesizeChunk.from_event(event)

                # To keep parity with wyoming-piper current behavior, feed by sentence:
                for sentence in self.sbd.add_chunk(stream_chunk.text):
                    if sentence.strip() == "":
                        return True
                    self._synthesize.text = sentence
                    await self._synthesize_with_engine(
                        sentence,
                        (self._synthesize.voice.name if self._synthesize.voice else getattr(self.cli_args, "voice", "en-US-Chirp3-HD-Charon")),
                        # stream path sends start/stop around each sentence as before
                        send_start=True,
                        send_stop=True,
                    )
                return True

            # Stream stop
            if SynthesizeStop.is_type(event.type):
                assert self._synthesize is not None
                final_text = self.sbd.finish()
                if final_text:
                    await self._synthesize_with_engine(
                        final_text,
                        (self._synthesize.voice.name if self._synthesize.voice else getattr(self.cli_args, "voice", "en-US-Chirp3-HD-Charon")),
                        send_start=True,
                        send_stop=True,
                    )

                await self.write_event(SynthesizeStopped().event())
                self.is_streaming = False
                _LOGGER.debug("Text stream stopped")
                return True

            return True

        except Exception as err:
            await self.write_event(
                Error(text=str(err), code=err.__class__.__name__).event()
            )
            _LOGGER.exception("Error in handler")
            raise

    # ------------------------------ Core synth -------------------------------

    async def _synthesize_with_engine(
        self,
        text: str,
        voice_name: str,
        send_start: bool = True,
        send_stop: bool = True,
    ) -> None:
        """Provider-agnostic streaming using the engine registry."""
        provider, engine, norm_voice = ENGINE_REGISTRY.pick(voice_name)
        _LOGGER.debug("Using engine=%s voice=%s", provider, norm_voice)

        announced = False
        async for kind, payload in engine.stream(text=text, voice_name=norm_voice, cli_args=self.cli_args):
            if kind == "format":
                fmt: AudioFormat = payload  # type: ignore[assignment]
                if send_start and not announced:
                    await self.write_event(
                        AudioStart(rate=fmt.rate, width=fmt.width, channels=fmt.channels).event()
                    )
                    announced = True
            elif kind == "chunk":
                data: bytes = payload  # type: ignore[assignment]
                # Use last-seen format or sensible defaults if not announced yet
                # (Engines always yield 'format' before the first 'chunk')
                await self.write_event(
                    AudioChunk(audio=data, rate=getattr(self.cli_args, "sample_rate", 22050), width=2, channels=1).event()
                )

        if send_stop and announced:
            await self.write_event(AudioStop().event())
