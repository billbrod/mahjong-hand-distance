from __future__ import annotations

import itertools

import numpy as np
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig
from mahjong.tile import TilesConverter

from .tile import DATA_IDX_MAPPER, FNAME_MAPPER, POSS_TILES, VALID_DATA, Tile

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

    def __init__(self, tiles: list[Tile | str] | np.ndarray, is_closed: bool = True):
        self.is_closed = is_closed
        if isinstance(tiles, list):
            if len(tiles) not in [13, 14]:
                msg = f"A hand has 13 or 14 tiles, not {len(tiles)}!"
                raise ValueError(msg)
            self.tiles = [t if isinstance(t, Tile) else Tile(t) for t in tiles]
            self._data = np.sum([t._data for t in self.tiles], 0)
        else:
            if tiles.sum() not in [13, 14]:
                msg = f"A hand has 13 or 14 tiles, not {tiles.sum()}!"
                raise ValueError(msg)
            if tiles.shape != (4, 9):
                msg = "In order to initialize from array, data must have shape (4, 9)!"
                raise ValueError(msg)
            self._data = tiles
            tiles = np.where(tiles.flatten())[0]
            self.tiles = [Tile(t) for t in tiles]

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
        # don't edit this in place
        tiles = list(self.tiles)
        try:
            discard_idx = tiles.index(discard_tile)
        except ValueError:
            msg = f"discard_tile {discard_tile} not found in hand!"
            raise ValueError(msg) from None
        tiles.pop(discard_idx)
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

        *WARNING*: Right now this is very inefficient, so that ``distance=1`` takes 13
        msec and ``distance=2`` takes 48 sec, and thus ``distance=3`` probably takes
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

    def _neighboring_hands_data_alt(
        self, data: np.ndarray, distance: int = 1
    ) -> np.ndarray:
        """ """
        poss_draws = np.bitwise_and(VALID_DATA, data < 4)
        poss_discards = data > 0

        poss_draws = np.expand_dims(POSS_TILES[poss_draws.flatten()], 1)
        poss_discards = np.expand_dims(POSS_TILES[poss_discards.flatten()], 0)

        poss_changes = poss_draws - poss_discards

        new_data = data + poss_changes
        new_data = new_data.reshape((-1, 4, 9))
        if distance == 1:
            return new_data
        return self._neighboring_hands_data(new_data, distance - 1)

    def _neighboring_hands_data(
        self, data: np.ndarray, distance: int = 1
    ) -> np.ndarray:
        """ """
        poss_draws = np.bitwise_and(VALID_DATA, data < 4)
        poss_discards = data > 0

        poss_draws = np.expand_dims(POSS_TILES[poss_draws.flatten()], 1)
        poss_discards = np.expand_dims(POSS_TILES[poss_discards.flatten()], 0)

        poss_changes = poss_draws - poss_discards

        new_data = data + poss_changes
        new_data = new_data.reshape((-1, 4, 9))
        if distance == 1:
            return new_data
        return self._neighboring_hands_data(new_data, distance - 1)

    def neighboring_hands_alt(
        self, distance: int = 1, previous_hands: np.ndarray | None = None
    ) -> Hands:
        """ """
        if previous_hands is None:
            # empty array for concatenating
            previous_hands = np.zeros((0, 4, 9))
        new_data = self._neighboring_hands_data(self._data, distance)
        new_data = new_data[new_data.any((-1, -2))]
        new_data = np.unique(np.concatenate((new_data, previous_hands), axis=0), axis=0)
        new_hands = Hands(*[Hand(h) for h in new_data])
        if distance == 1:
            return new_hands
        return Hands.concat(
            [h.neighboring_hands_alt(distance - 1, new_data) for h in new_hands]
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
