from __future__ import annotations

from importlib import resources

__all__ = ["get"]


def __dir__() -> list[str]:
    return __all__


IMAGES = {}
for f in resources.files(__name__).iterdir():
    if f.is_file():
        IMAGES[f.stem] = f.open().read()


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
    try:
        return IMAGES[item_name]
    except KeyError:
        msg = f"No svg named {item_name}!"
        raise ValueError(msg) from None
