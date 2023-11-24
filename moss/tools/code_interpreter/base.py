from __future__ import annotations

from typing import Protocol

from moss.tools.code_interpreter.output import RunOutput


class CodeInterpreter(Protocol):
    def run(self, code: str) -> list[RunOutput]:
        ...
