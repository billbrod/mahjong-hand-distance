from __future__ import annotations

import numpy as np

from .tile import Tile


class Hand:
    """ """

    def __init__(self, tiles: list[Tile | str]):
        if len(tiles) not in [13, 14]:
            msg = f"A hand has 13 or 14 tiles, not {len(tiles)}!"
            raise ValueError(msg)
        self.tiles = [t if isinstance(t, Tile) else Tile(t) for t in tiles]
        self._data = np.expand_dims(np.sum([t._data for t in self.tiles], 0), 0)
        self._svg = "<div>" + "".join([t._svg for t in self.tiles]) + "</div>"

    def _repr_html_(self):
        return self._svg

    def __sub__(self, other):
        return HandDiff(self._data - other._data)

    def distance(self, other):
        return (self - other).distance


class HandDiff:
    """ """

    def __init__(self, data: np.ndarray):
        self._data = data
        self.draw_tiles = []
        self.discard_tiles = []
        idx = np.where(data)
        for _, s, v in zip(*idx, strict=False):
            tile_data = np.zeros((4, 9))
            tile_data[s, v] = 1
            if data[0, s, v] == 1:
                self.draw_tiles.append(Tile.from_data(tile_data))
            elif data[0, s, v] == -1:
                self.discard_tiles.append(Tile.from_data(tile_data))
        if len(idx[0]):
            self._svg = (
                "<div><h3>Draw: </h3>"
                + "".join([t._svg for t in self.draw_tiles])
                + "<h3>Discard:</h3>"
                + "".join([t._svg for t in self.discard_tiles])
                + "</div>"
            )
        else:
            self._svg = ""

    def _repr_html_(self):
        return self._svg

    @property
    def distance(self):
        return self._data.clip(0).sum((-1, -2))
