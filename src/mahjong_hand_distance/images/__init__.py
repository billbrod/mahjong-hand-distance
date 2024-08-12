from __future__ import annotations

from importlib import resources


def get(item_name: str):
    """Retrieve the svg contents of the file that matches the given item name

    Parameters
    ----------
    item_name :
        The name of the item to find the file for, without specifying the file extension.

    Returns
    -------
    :
        The filename matching the `item_name` with its extension.

    Raises
    ------
    AssertionError
        If no files or more than one file match the `item_name`.

    """
    fhs = [
        f
        for f in resources.files("mahjong_hand_distance.images").iterdir()
        if f.name == f"{item_name}.svg"
    ]
    if len(fhs) != 1:
        msg = f"Expected exactly one file for {item_name}, but found {len(fhs)}."
        raise ValueError(msg)
    with fhs[0].open() as f:
        return f.read()
