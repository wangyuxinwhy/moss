from typing import Any, Dict, List, Literal

from pydantic import BaseModel


class MIMEPart(BaseModel):
    mime_type: str
    content: Any


class RunOutput(BaseModel):
    type: str
    content: Any
    metadata: Dict[str, Any] = {}


class StreamContent(BaseModel):
    name: Literal['stdout', 'stderr']
    text: str


class StreamOutput(RunOutput):
    type: Literal['stream'] = 'stream'
    content: StreamContent


class DisplayOutput(RunOutput):
    type: Literal['display_data'] = 'display_data'
    content: List[MIMEPart]


class ExecuteResultOutput(RunOutput):
    type: Literal['execute_result'] = 'execute_result'
    content: List[MIMEPart]


class ErrorContent(BaseModel):
    name: str
    value: str
    trace_back: List[str]


class ErrorOutput(RunOutput):
    type: Literal['error'] = 'error'
    content: ErrorContent
