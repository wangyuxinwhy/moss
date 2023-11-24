from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Any, List

from generate import OpenAIChat, OpenAIChatParameters
from generate.chat_completion import ChatCompletionOutput, function
from generate.chat_completion.message import (
    AssistantMessage,
    Message,
    Prompt,
    SystemMessage,
    ToolCall,
    ToolCallsMessage,
    ToolMessage,
    ensure_messages,
)

from moss.jupyter_env import JupyterEnv


@function
def python(code: str) -> str:
    return code


class Agent:
    def __init__(
        self,
        agent_name: str = 'moss',
        language: str = '中文',
        model: str = 'gpt-4-1106-preview',
        max_calls_per_turn: int = 10,
        env: JupyterEnv | None = None,
    ) -> None:
        self.agent_name = agent_name
        self.language = language
        self.chat_model = OpenAIChat(
            model=model,
            parameters=OpenAIChatParameters(tools=[{'type': 'function', 'function': python.json_schema}], temperature=0),
        )
        self.max_calls_per_turn = max_calls_per_turn
        self.env = env or JupyterEnv()

        self.system_prompt = self.get_system_prompt()
        self.history: list[Message] = []
        self.model_ouptuts: list[ChatCompletionOutput] = []
        self._call_count = 0
        self._temp_kwargs = {}

    def get_system_prompt(self) -> str:
        agent_prompt = (
            f"""You are {self.agent_name}, an assistant proficient in python code, you are set up in a Jupyter environment.
            use {self.language} to chat with me."""
        )
        env_prompt = self.env.generate_env_prompt()
        return agent_prompt + '\n' + env_prompt

    def recall_memory(self) -> str:
        return """name: Alice
department: 人力资源部
intrested_stock: META, Google, Coca-cola
"""

    def chat(self, user_input: Prompt) -> None:
        self._call_count = 0

        messages = list(ensure_messages(user_input))
        self.history.extend(messages)
        # memory_message = UserMessage(content='This information may be helpful to you.' + self.recall_memory())
        # self.history.append(memory_message)
        output = self.run_completion()
        print(output.reply)

    def run_completion(self) -> ChatCompletionOutput:
        while True:
            model_output = self.chat_model.generate(
                [SystemMessage(content=self.system_prompt)] + self.history, **self._temp_kwargs
            )
            self._temp_kwargs.clear()
            self._handle_model_output(model_output)
            if isinstance(model_output.last_message, AssistantMessage):
                return model_output

    def _handle_model_output(self, model_output: ChatCompletionOutput, **kwargs: Any) -> None:
        if not model_output.last_message:
            raise RuntimeError('messages in model output is empty.', model_output.model_dump())

        self.model_ouptuts.append(model_output)
        self.history.extend(model_output.messages)

        if isinstance(model_output.last_message, ToolCallsMessage):
            self._call_count += 1
            if self._call_count > self.max_calls_per_turn:
                raise RuntimeError('Maximum number of tool calls reached.')
            tool_calls = model_output.last_message.content
            self._handle_tool_calls(tool_calls, **kwargs)

    def _handle_tool_calls(self, tool_calls: List[ToolCall], **kwargs: Any) -> None:
        tool_messages: list[ToolMessage] = []
        for tool_call in tool_calls:
            if tool_call.function.name != 'python':
                self.history = self.history[:-1]
                self._temp_kwargs['tool_choice'] = {'type': 'function', 'function': {'name': 'python'}}
                continue

            try:
                arguments = json.loads(tool_call.function.arguments, strict=False)
            except JSONDecodeError:
                arguments = {'code': tool_call.function.arguments}
            function_output = self.env.run_cell(**arguments)  # type: ignore
            tool_message = ToolMessage(
                tool_call_id=tool_call.id, name=tool_call.function.name, content=json.dumps(function_output, ensure_ascii=False)
            )
            tool_messages.append(tool_message)
        self.history.extend(tool_messages)

    def reset(self) -> None:
        self.history: list[Message] = [SystemMessage(content=self.system_prompt)]
        self.model_ouptuts.clear()

    @property
    def current_cost(self) -> float:
        return sum(i.cost for i in self.model_ouptuts if i.cost is not None)
