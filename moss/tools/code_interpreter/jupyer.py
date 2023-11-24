from __future__ import annotations

from typing import Any

import nbformat
from nbclient import NotebookClient
from nbformat import NotebookNode

from moss.tools.code_interpreter.base import CodeInterpreter
from moss.tools.code_interpreter.output import (
    DisplayOutput,
    ErrorContent,
    ErrorOutput,
    ExecuteResultOutput,
    MIMEPart,
    RunOutput,
    StreamContent,
    StreamOutput,
)


def convert_jupyter_cell_output(cell_output: dict[str, Any]) -> RunOutput:
    if cell_output['output_type'] == 'stream':
        return StreamOutput(
            content=StreamContent(name=cell_output['name'], text=cell_output['text']),
            metadata=cell_output.get('metadata', {}),
        )

    if cell_output['output_type'] == 'display_data':
        return DisplayOutput(
            content=[MIMEPart(mime_type=mime_type, content=content) for mime_type, content in cell_output['data'].items()],
            metadata=cell_output.get('metadata', {}),
        )

    if cell_output['output_type'] == 'execute_result':
        return ExecuteResultOutput(
            content=[MIMEPart(mime_type=mime_type, content=content) for mime_type, content in cell_output['data'].items()],
            metadata=cell_output.get('metadata', {}),
        )

    if cell_output['output_type'] == 'error':
        return ErrorOutput(
            content=ErrorContent(
                name=cell_output['ename'],
                value=cell_output['evalue'],
                trace_back=cell_output['traceback'],
            ),
            metadata=cell_output.get('metadata', {}),
        )

    raise ValueError(f'Unknown output type: {cell_output["output_type"]}')


class JupyterCodeInterpreter(CodeInterpreter):
    def __init__(
        self,
        kernel_name: str = 'python3',
        workspace_dir: str | None = None,
        timeout: int = 60,
        interrupt_on_timeout: bool = True,
        allow_errors: bool = True,
        record_timing: bool = False,
    ) -> None:
        empty_notebook = {'cells': [], 'metadata': {}, 'nbformat': 4, 'nbformat_minor': 2}
        self.noteboook_client = NotebookClient(
            NotebookNode(empty_notebook),
            kernel_name=kernel_name,
            timeout=timeout,
            interrupt_on_timeout=interrupt_on_timeout,
            allow_errors=allow_errors,
            record_timing=record_timing,
            resources={'metadata': {'path': workspace_dir}},
        )
        self.noteboook_client.create_kernel_manager()
        self.noteboook_client.start_new_kernel()
        self.noteboook_client.start_new_kernel_client()
        self.index = 0

    def stop(self) -> None:
        self.noteboook_client._cleanup_kernel()

    def run(self, code: str) -> list[RunOutput]:
        cell = NotebookNode({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': code})
        self.noteboook_client.nb.cells.append(cell)
        executed_cell = self.noteboook_client.execute_cell(cell, cell_index=self.index)
        self.index += 1
        return [convert_jupyter_cell_output(output) for output in executed_cell['outputs']]

    def save_to_notebook(self, path: str) -> None:
        nbformat.write(self.noteboook_client.nb, path)
