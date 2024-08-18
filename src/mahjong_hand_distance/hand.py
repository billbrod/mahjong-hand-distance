from __future__ import annotations

import itertools

import numpy as np
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig
from mahjong.tile import TilesConverter

from .tile import DATA_IDX_MAPPER, FNAME_MAPPER, VALID_DATA, Tile

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

    def __str__(self) -> str:
        return "[" + ",".join([str(t) for t in self.tiles]) + "]"

    def __repr__(self) -> str:
        return self.__str__()

    def _repr_html_(self) -> str:
        return "<div>" + "".join([t._svg for t in self.tiles]) + "</div>"

    def __add__(self, other: Hand | Hands) -> Hands:
        if isinstance(other, Hand):
            return Hands(self, other)
        return other + self

    def __sub__(self, other: Hand | Hands) -> HandDiff | HandsDiff:
        if isinstance(other, Hand):
            return HandDiff(self._data - other._data)
        if isinstance(other, Hands):
            return HandsDiff(self._data - other._data)
        msg = f"can't take difference with type {type(other)}"
        raise ValueError(msg)

    def distance(self, other: Hand) -> int | np.ndarray:
        """Compute the distance between two hands."""
        return (self - other).distance

    def draw(self, draw_tile: Tile | str | int, discard_tile: Tile | str | int) -> Hand:
        """Draw and discard tile."""
        if not isinstance(draw_tile, Tile):
            draw_tile = Tile(draw_tile)
        if not isinstance(discard_tile, Tile):
            discard_tile = Tile(discard_tile)
        if not any(t == discard_tile for t in self.tiles):
            msg = f"discard_tile {discard_tile} not found in hand!"
            raise ValueError(msg)
        # don't edit this in place
        tiles = list(self.tiles)
        tiles.remove(discard_tile)
        tiles.append(draw_tile)
        # return tiles
        return Hand(tiles)

    def __getitem__(self, tile_no) -> Tile:
        return self.tiles[tile_no]

    @staticmethod
    def _convert_to_136_array(tiles: list[Tile]) -> list[int]:
        tiles_dict = {"honors": "", "man": "", "pin": "", "sou": ""}
        for t in tiles:
            suit = FNAME_MAPPER[t.suit].lower()
            val = t.value
            if suit not in ["man", "pin", "sou"]:
                suit = "honors"
                val = DATA_IDX_MAPPER[t.value] + 1
            tiles_dict[suit] += str(val)
        return TilesConverter.string_to_136_array(**tiles_dict)

    def score(self, self_drawn: bool = False) -> dict:
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

    def neighboring_hands(self, distance: int = 1) -> Hands:
        """Figure out how the hands that are ``distance`` number of draws away

        *WARNING*: Right now this is very inefficient, so that ``distance=1`` takes 90
        msec and ``distance=2`` takes 90 sec, and thus ``distance=3`` probably takes 25
        hours.

        """
        poss_draws = np.bitwise_and(VALID_DATA, self._data < 4)
        poss_draws = np.where(poss_draws.flatten())[0]
        poss_discards = np.where((self._data > 0).flatten())[0]
        hands = []
        for draw, discard in itertools.product(poss_draws, poss_discards):
            hands.append(self.draw(draw, discard))
        neighboring_hands = Hands(*hands)
        if distance == 1:
            return neighboring_hands
        return Hands.concat(
            [h.neighboring_hands(distance - 1) for h in neighboring_hands]
        )


class Hands:
    """Multiple hands"""

    def __init__(self, *hands: Hand | Hands):
        self.hands = hands
        self._data = np.stack([h._data for h in hands])

    def __add__(self, other: Hand | Hands) -> Hands:
        if isinstance(other, Hand):
            return Hands(*self.hands, other)
        return Hands(*self.hands, *other.hands)

    def __str__(self) -> str:
        return "[" + "\n".join([str(t) for t in self.hands]) + "]"

    def __repr__(self) -> str:
        return self.__str__()

    def _repr_html_(self):
        diff_svg = [
            f"<h2>Hand {h+1}</h2>{hand._repr_html_()}"
            for h, hand in enumerate(self.hands)
        ]
        return f"<div>{''.join(diff_svg)}</div>"

    def __getitem__(self, hand_no):
        to_return = self.hands[hand_no]
        if isinstance(to_return, Hand):
            return to_return
        return Hands(*to_return)

    def __len__(self):
        return self._data.shape[0]

    @classmethod
    def concat(cls, hands: list[Hands]) -> Hands:
        if len(hands) == 2:
            return hands[0] + hands[1]
        return hands[0] + cls.concat(hands[1:])


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
                tiles = abs(flat_data[i]) * Tile(i)
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
