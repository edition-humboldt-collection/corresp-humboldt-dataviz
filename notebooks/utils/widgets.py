import ipywidgets as widgets
from nested_lookup import nested_lookup


def createDropdown(desc: str, data:list ):
    """
    Create a Dropdown menu 
    :param desc: str
    :param data: list
    :return: Dropdown menu
    :rtype: widget
    """
    w = widgets.Dropdown(
    options=sorted(set(data)),
    value=None,
    description=desc,
    disabled=False
    )
    return w


def createCheckBox(desc:str, value:bool):
    """
    Create a checkbox 
    :param desc: str
    :param value: bool
    :return: Checkbox
    :rtype: widget
    """
    w = widgets.Checkbox(
    value=value,
    description=desc,
    disabled=False,
    indent=False
    )
    return w
    

def createButton(desc:str, style: str):
    """
    Create a button 
    :param desc: str
    :param style: str
    :return: Button
    :rtype: widget
    """
    w = widgets.Button(
    value=False,
    description=desc,
    disabled=False,
    button_style=style, # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Description',
    )
    return w

