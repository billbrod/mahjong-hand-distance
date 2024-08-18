from __future__ import annotations

import numpy as np

from . import images

SUIT_MAPPER = {"c": "crack", "b": "boo", "d": "dot"}
FNAME_MAPPER = {
    "crack": "Man",
    "dot": "Pin",
    "boo": "Sou",
    "red": "Chun",
    "green": "Hatsu",
    "white": "Haku",
    "south": "Nan",
    "north": "Pei",
    "west": "Shaa",
    "east": "Ton",
}
DATA_SUIT_MAPPER = {"crack": 0, "boo": 1, "dot": 2, "honor": 3}
DATA_SUIT_MAPPER_REV = {v: k for k, v in DATA_SUIT_MAPPER.items()}
DATA_IDX_MAPPER = {
    "east": 0,
    "south": 1,
    "west": 2,
    "north": 3,
    "white": 4,
    "green": 5,
    "red": 6,
}
DATA_IDX_MAPPER_REV = {v: k for k, v in DATA_IDX_MAPPER.items()}


class Tile:
    """Class for representing mahjong tile.

    Arguments
    ----------
    tile :
        Representation of the tile.

        - If a string: If a numbered tile, format is "#S", where # is a number between 1
          and 9, and S is a one-letter code giving the suit: c (for crack/characters), d
          (for dots), and b (for boo / bamboo). If a wind, should be just the direction.
          If a dragon, should be just the color.

        - If an int:

          - 0-8: 1 through 9 crack
          - 9-17: 1 through 9 boo
          - 18-26: 1 through 9 dot
          - 27-33: east wind, south wind, west wind, north wind, white dragon, green
                   dragon, red dragon

        - If an array:

    """

    def __init__(self, tile: str | int | np.ndarray):
        if isinstance(tile, str):
            self._from_str(tile)
        elif isinstance(tile, int):
            self._from_int(tile)
        elif isinstance(tile, np.ndarray):
            self._from_data(tile)

    def __str__(self):
        return self._str_rep

    def __repr__(self):
        return self.__str__()

    def _repr_svg_(self):
        return self._svg

    def __eq__(self, other):
        return (self._data == other._data).all()

    def __mul__(self, other):
        if isinstance(other, int):
            return other * [self]
        msg = f"unsupported operand type(s) for *: {type(other)} and 'Tile'"
        raise TypeError(msg)

    __rmul__ = __mul__

    def _from_str(self, tile: str):
        self._data = np.zeros((4, 9))
        if len(tile) == 2:
            self.value = int(tile[0])
            if self.value < 1 or self.value > 9:
                msg = "Value must lie between 1 and 9!"
                raise ValueError(msg)
            if tile[1] not in ["b", "c", "d"]:
                msg = "Suit must be one of c, b, or d!"
                raise ValueError(msg)
            self.suit = SUIT_MAPPER[tile[1]]
            self.name = f"{self.value} {self.suit}"
            img_fname = f"{FNAME_MAPPER[self.suit]}{self.value}"
            self._data[DATA_SUIT_MAPPER[self.suit], self.value - 1] = 1
        else:
            self.value = tile
            self.suit = "honor"
            if tile in ["east", "north", "west", "south"]:
                self.name = f"{self.value} wind"
            elif tile in ["red", "green", "white"]:
                self.name = f"{self.value} dragon"
            else:
                msg = f"Unsure what to do with tile {tile}!"
                raise ValueError(msg)
            img_fname = FNAME_MAPPER[self.value]
            self._data[DATA_SUIT_MAPPER[self.suit], DATA_IDX_MAPPER[self.value]] = 1
        self._str_rep = tile
        self._svg = images.get(img_fname)

    def _from_data(self, data: np.ndarray):
        if data.sum() != 1:
            msg = "In order to initialize from array, data must have a single 1 value!"
            raise ValueError(msg)
        if data.shape != (4, 9):
            msg = "In order to initialize from array, data must have shape (4, 9)!"
            raise ValueError(msg)
        self._from_int(np.where(data.flatten())[0][0])

    def _from_int(self, index: int):
        """Initialize from integer index

        index should be an integer between 0 and 33 (inclusive):

        - 0-8: 1 through 9 crack
        - 9-17: 1 through 9 boo
        - 18-26: 1 through 9 dot
        - 27-33: east wind, south wind, west wind, north wind, white dragon, green
                 dragon, red dragon

        """
        if index < 0 or index > 33:
            msg = "index must lie between 0 and 33, inclusive"
            raise ValueError(msg)
        suit = index // 9
        val = index % 9
        if suit == 3:
            self._from_str(DATA_IDX_MAPPER_REV[val])
        else:
            suit = DATA_SUIT_MAPPER_REV[suit]
            self._from_str(f"{val+1}{suit[0]}")
