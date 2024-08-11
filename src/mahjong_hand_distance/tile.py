#!/usr/bin/env python3

import numpy as np

SUIT_MAPPER = {'c': 'crack', 'b': 'boo', 'd': 'dot'}

class Tile:
    """
    """
    def __init__(self, tile: str):
        if len(tile) == 2:
            self.value = int(tile[0])
            self.suit = SUIT_MAPPER[tile[1]]
        else:
            self.value = tile
            self.suit = 'honor'
        self._str_rep = tile

    def __str__(self):
        return self._str_rep

    def __repr__(self):
        return self.__str__()
