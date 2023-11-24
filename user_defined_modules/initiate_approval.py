"""提起审批

Example:
    >>> from initiate_approval import initiate_leave_approval
    >>> initiate_leave_approval(leave_type='事假')
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal


def initiate_leave_approval(
    leave_type: Literal['事假', '病假', '年假'] | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> None:
    # Ipywidgets
    from IPython.display import display
    from ipywidgets import widgets

    leave_type_dropdown = widgets.Dropdown(description='请假类型', options=['事假', '病假', '年假'], value=leave_type)
    start_date_picker = widgets.DatePicker(description='开始时间', value=start_date)
    end_date_picker = widgets.DatePicker(description='结束时间', value=end_date)
    submit_button = widgets.Button(description='提交')
    form = widgets.VBox([leave_type_dropdown, start_date_picker, end_date_picker, submit_button])
    display(form)


__all__ = ['initiate_leave_approval']
