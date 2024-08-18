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
        self._data = np.sum([t._data for t in self.tiles], 0)

    def __str__(self):
        return "[" + ",".join([str(t) for t in self.tiles]) + "]"

    def __repr__(self):
        return self.__str__()

    def _repr_html_(self):
        return "<div>" + "".join([t._svg for t in self.tiles]) + "</div>"

    def __sub__(self, other: Hand | Hands) -> HandDiff | HandsDiff:
        if isinstance(other, Hand):
            return HandDiff(self._data - other._data)
        if isinstance(other, Hands):
            return HandsDiff(self._data - other._data)
        msg = f"can't take difference with type {type(other)}"
        raise ValueError(msg)

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


class Hands:
    """Multiple hands"""

    def __init__(self, *hands: Hand):
        self.hands = hands
        self._data = np.stack([h._data for h in hands])

    def _repr_html_(self):
        diff_svg = [
            f"<h2>Hand {h+1}</h2>{hand._repr_html_()}"
            for h, hand in enumerate(self.hands)
        ]
        return f"<div>{''.join(diff_svg)}</div>"

    def __getitem__(self, hand_no):
        return self.hands[hand_no]


class HandDiff:
    """Difference between two hands.

    Represents the difference between two hands, enables the computation of
    distance (number of tiles to draw to get from one hand to another).

    Shouldn't be initialized directly, but rather by subtracting two Hand
    objects.

    Parameters
    ----------
    data :
        Data representation of tiles, a 2d array of shape (4, 9), where suits are
        indexed on the first dimension and value on the second.

    """

    def __init__(self, data: np.ndarray):
        if data.ndim != 2:
            msg = "data must be 2d!"
            raise ValueError(msg)
        self._data = data.astype(int)
        self.draw_tiles = []
        self.discard_tiles = []
        flat_data = self._data.flatten()
        idx = np.where(flat_data)[0]
        if len(idx) == 0:
            self._svg = "<div><h3>Identical hands</h3></div>"
        else:
            for i in idx:
                tiles = abs(flat_data[i]) * Tile.from_int(i)
                if flat_data[i] < 0:
                    self.draw_tiles.extend(tiles)
                else:
                    self.discard_tiles.extend(tiles)
            self._svg = (
                "<div><h3>Draw: </h3>"
                + "".join([t._svg for t in self.draw_tiles])
                + "</div><div><h3>Discard:</h3>"
                + "".join([t._svg for t in self.discard_tiles])
                + "</div>"
            )

    def _repr_html_(self):
        return self._svg

    @property
    def distance(self):
        return self._data.clip(0).sum((-1, -2))


class HandsDiff(Hands, HandDiff):
    """Represent difference of hands"""

    def __init__(self, data: np.ndarray):
        self._data = data.astype(int)
        self.hands = [HandDiff(d) for d in self._data]
