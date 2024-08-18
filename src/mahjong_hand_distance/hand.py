from __future__ import annotations

import numpy as np
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig
from mahjong.tile import TilesConverter

from .tile import DATA_IDX_MAPPER, FNAME_MAPPER, Tile

CALCULATOR = HandCalculator()


class Hand:
    """Full hand of mahjong tiles.

    Parameters
    ----------
    tiles :
        List of tiles, can contain either Tile objects or their string
        representations. Must be of length 13 or 14.
    is_closed :
        Whether the hand is closed or not

    """

    def __init__(self, tiles: list[Tile | str], is_closed: bool = True):
        self.is_closed = is_closed
        if len(tiles) not in [13, 14]:
            msg = f"A hand has 13 or 14 tiles, not {len(tiles)}!"
            raise ValueError(msg)
        self.tiles = [t if isinstance(t, Tile) else Tile(t) for t in tiles]
        self._data = np.expand_dims(np.sum([t._data for t in self.tiles], 0), 0)

    def _repr_html_(self):
        return "<div>" + "".join([t._svg for t in self.tiles]) + "</div>"

    def __sub__(self, other: Hand) -> HandDiff:
        return HandDiff(self._data - other._data)

    def distance(self, other: Hand) -> float:
        """Compute the distance between two hands."""
        return (self - other).distance

    def draw(self, draw_tile: Tile | str, discard_tile: Tile | str) -> Hand:
        """Draw and discard tile."""
        if not isinstance(draw_tile, Tile):
            draw_tile = Tile(draw_tile)
        if not isinstance(discard_tile, Tile):
            discard_tile = Tile(discard_tile)
        if not any(t == discard_tile for t in self.tiles):
            msg = f"discard_tile {discard_tile} not found in hand!"
            raise ValueError(msg)
        self.tiles.remove(discard_tile)
        self.tiles.append(draw_tile)
        self._data = self._data + draw_tile._data - discard_tile._data
        return self

    def __getitem__(self, tile_no):
        return self.tiles[tile_no]

    @staticmethod
    def _convert_to_136_array(tiles: list[Tile]):
        tiles_dict = {"honors": "", "man": "", "pin": "", "sou": ""}
        for t in tiles:
            suit = FNAME_MAPPER[t.suit].lower()
            val = t.value
            if suit not in ["man", "pin", "sou"]:
                suit = "honors"
                val = DATA_IDX_MAPPER[t.value] + 1
            tiles_dict[suit] += str(val)
        return TilesConverter.string_to_136_array(**tiles_dict)

    def score(self, self_drawn: bool = False):
        """Score hand."""
        if not self_drawn:
            self.is_closed = False
        winning_tile = self._convert_to_136_array([self.tiles[-1]])[0]
        tiles = self._convert_to_136_array(self.tiles)
        result = CALCULATOR.estimate_hand_value(
            tiles, winning_tile, config=HandConfig(is_tsumo=self_drawn)
        )
        result = {
            k: getattr(result, k) for k in ["han", "fu", "cost", "yaku", "fu_details"]
        }
        result["score"] = result.pop("cost")
        for k in ["han", "fu", "score"]:
            if result[k] is None:
                result[k] = 0
        if result["yaku"] is None:
            result["yaku"] = 0
        if result["fu_details"] is None:
            result["fu_details"] = []
        return result


class HandDiff:
    """Difference between two hands.

    Represents the difference between two hands, enables the computation of
    distance (number of tiles to draw to get from one hand to another).

    Shouldn't be initialized directly, but rather by subtracting two Hand
    objects.

    Parameters
    ----------
    data :
        Data representation of tiles, a 3d array of shape (n_hands, 4, 9),
        where suits are indexed on the second dimension and value on the third.

    """

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
                + "</div><div><h3>Discard:</h3>"
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
