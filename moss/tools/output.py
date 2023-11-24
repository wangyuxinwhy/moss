from typing import Any, Dict, List, Union

from pydantic import BaseModel


class Image(BaseModel):
    image: bytes
    image_format: str


class Audio(BaseModel):
    audio: bytes
    audio_format: str


class ToolOutput(BaseModel):
    output_for_chat_model: str = ''
    content: List[Union[Image, Audio]] = []
    extra: Dict[str, Any] = {}
