from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import groupby
from typing import Iterable, Literal, Sequence, cast

from moss.tools.code_interpreter.output import (
    MIMEPart,
    RunOutput,
    StreamOutput,
)


class RunOutputsProcessor(ABC):
    @abstractmethod
    def process(self, outputs: Sequence[RunOutput]) -> str:
        ...


def truncate(text: str, max_length: int, mode: Literal['head', 'tail', 'middle'] = 'middle') -> str:
    if len(text) <= max_length:
        return text

    if mode == 'head':
        return '...' + text[-max_length + 3 :]
    if mode == 'tail':
        return text[: max_length - 3] + '...'
    if mode == 'middle':
        return text[: max_length // 2 - 2] + '...' + text[-max_length // 2 + 1 :]

    raise ValueError(f'Unknown mode: {mode}')


class MarkdownRunOutputsProcessor(RunOutputsProcessor):
    def __init__(
        self,
        max_streams: int = 4,
        max_charecters_per_output: int = 500,
        truncate_mode: Literal['head', 'tail', 'middle'] = 'middle',
    ) -> None:
        self.max_streams = max_streams
        self.max_charecters_per_output = max_charecters_per_output
        self.truncate_mode: Literal['head', 'tail', 'middle'] = truncate_mode

    def process(self, outputs: Sequence[RunOutput]) -> str:
        texts = []
        for output_type, group in groupby(outputs, key=lambda output: output.type):
            if output_type == 'stream':
                group = cast(Iterable[StreamOutput], group)
                texts.append(self._process_stream_outputs(group))
            elif output_type in ('display_data', 'execute_result'):
                for output in group:
                    mime_parts = output.content
                    texts.append(self._process_mime_parts(mime_parts))
            elif output_type == 'error':
                for output in group:
                    text = self._process_error_output(output)
                    texts.append(text)
            else:
                raise ValueError(f'Unknown output type: {output_type}')
        return '\n'.join(texts)

    def _process_stream_outputs(self, outputs: Iterable[StreamOutput]) -> str:
        outputs = list(outputs)
        if len(outputs) >= self.max_streams:
            outputs = outputs[:2] + outputs[-2:]
        texts = []
        for output in outputs:
            text = output.content.text
            text = truncate(text, self.max_charecters_per_output, self.truncate_mode)
            texts.append(text)
        return '\n'.join(texts)

    def _process_mime_parts(self, mime_parts: list[MIMEPart]) -> str:
        texts = []
        for mime_part in mime_parts:
            if mime_part.mime_type.startswith('text/'):
                text = mime_part.content
                text = truncate(text, self.max_charecters_per_output, self.truncate_mode)
                texts.append(text)
            else:
                text = f'will display "{mime_part.mime_type}" to user, successful run!'
                texts.append(text)
        return '\n'.join(texts)

    def _process_error_output(self, output: RunOutput) -> str:
        return f'# Error\nError Name: {output.content.name}\nError Value: {output.content.value}\n'
