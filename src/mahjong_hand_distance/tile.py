from __future__ import annotations

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


class Tile:
    """Class for representing mahjong tile.

    Arguments
    ----------
    tile :
        String representation of the tile. If a numbered tile, format is "#S",
        where # is a number between 1 and 9, and S is a one-letter code giving
        the suit: c (for crack/characters), d (for dots), and b (for boo /
        bamboo). If a wind, should be just the direction. If a dragon, should
        be just the color.

    """

    def __init__(self, tile: str):
        if len(tile) == 2:
            self.value = int(tile[0])
            self.suit = SUIT_MAPPER[tile[1]]
            self.name = f"{self.value} {self.suit}"
            img_fname = f"{FNAME_MAPPER[self.suit]}{self.value}"
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
        self._str_rep = tile
        self._svg = images.get(img_fname)

    def __str__(self):
        return self._str_rep

    def __repr__(self):
        return self.__str__()

    def _repr_svg_(self):
        return self._svg
