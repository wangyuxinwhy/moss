from __future__ import annotations

from IPython import get_ipython
from pydantic import BaseModel

from moss.tools.code_interpreter.jupyer import JupyterCodeInterpreter
from moss.tools.code_interpreter.output_processor import MarkdownRunOutputsProcessor


class PackageInfo(BaseModel):
    name: str
    introduction: str = ''

    def to_prompt(self) -> str:
        if self.introduction:
            return f'- {self.name} | {self.introduction}'
        return f'- {self.name}'


class FileInfo(BaseModel):
    name: str
    path: str
    introduction: str = ''

    def to_prompt(self) -> str:
        if self.introduction:
            return """name: {name}
path: {path}
introduction: {introduction}""".format(
                name=self.name,
                path=self.path,
                introduction=self.introduction,
            )
        return """name: {name}
path: {path}""".format(
            name=self.name,
            path=self.path,
        )


python_tool_prompt = """
# Tools
## Python
When you send code to Python, it will be executed in a *stateful* Jupyter notebook environment.
Python tool will respond with the output of the execution or time out after 60.0 seconds.
The drive at './data/' can be used to save and persist user files.
"""

file_info_template = """name: {name}
path: {path}
introduction: {introduction}
---"""

python_prompt = """# Tool: Python
When you send code to Python, it will be executed in a *stateful* Jupyter notebook environment.
Python tool will respond with the output of the execution or time out after 60.0 seconds.
The drive at './data/' can be used to save and persist user files.
"""
user_files_prompt = """# User Files
{files_info}
"""
user_favored_packages_prompt = """# User Favored Packages
{favored_packages_info}
"""
user_private_packages_prompt = """# User Private Packages
User provides some python packages in Python jupyter environment to help you complete tasks.
In python code, You can import and use these packages, just like regular python packages.
When the user's task can be completed through these packages, please prioritize using these packages.
Before using it, you MUST first obtain help information for these packages by calling the help() function. Like this
```python
import <package_name>
help(<package_name>)
```

The following is a list of user-defined packages:
{user_defined_packages_info}
"""


class JupyterEnv:
    def __init__(
        self,
        code_kenel: JupyterCodeInterpreter | None = None,
        run_outputs_processor: MarkdownRunOutputsProcessor | None = None,
        favored_packages: list[PackageInfo] | None = None,
        private_packages: list[PackageInfo] | None = None,
        files: list[FileInfo] | None = None,
        rend_applications: bool = False,
    ) -> None:
        self.code_kenel = code_kenel or JupyterCodeInterpreter()
        self.run_outputs_processor = run_outputs_processor or MarkdownRunOutputsProcessor()
        self.favored_packages = favored_packages or []
        self.user_defined_packages = private_packages or []
        self.files = files or []
        self.rend_applications = rend_applications

    def run_cell(self, code: str, slient: bool = False) -> str:
        if self.rend_applications:
            ip = get_ipython()
            if ip is not None:
                ip.run_cell(code, silent=slient)
        outputs = self.code_kenel.run(code)
        return self.run_outputs_processor.process(outputs)

    def generate_env_prompt(self) -> str:
        files_info = '---'.join(file.to_prompt() for file in self.files)
        favored_packages_info = '\n'.join(package.to_prompt() for package in self.favored_packages)

        user_defined_packages_info = '\n'.join(package.to_prompt() for package in self.user_defined_packages)
        prompt = python_prompt
        if files_info:
            prompt += user_files_prompt.format(files_info=files_info)
        if favored_packages_info:
            prompt += user_favored_packages_prompt.format(favored_packages_info=favored_packages_info)
        if user_defined_packages_info:
            prompt += user_private_packages_prompt.format(user_defined_packages_info=user_defined_packages_info)
        return prompt

    def save_to_notebook(self, file_path: str) -> None:
        self.code_kenel.save_to_notebook(file_path)
