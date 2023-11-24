"""
A Python Package to help moss record information.

Examples:
>>> from moss import memory
>>> memory.record('user_name', 'Alice')
>>> memory.recall('name of user')
"""

import json
from pathlib import Path
from typing import Any, Dict


def _read_from_disk() -> Dict[str, Any]:
    """Reads the memory from disk."""
    memory_file = Path('~/.cache').expanduser() / 'memory.json'
    return json.loads(memory_file.read_text())


_memory = _read_from_disk()


def recall(query: str) -> Dict[str, str]:
    """Searches the memory for the given query."""
    return _memory


def record(key: str, value: str) -> None:
    """Remembers the given value for the given key."""
    _memory[key] = value
    print(f'recorded {key} as {value}')
    memory_file = Path('~/.cache').expanduser() / 'memory.json'
    memory_file.write_text(json.dumps(_memory))


__all__ = ['recall', 'record']
