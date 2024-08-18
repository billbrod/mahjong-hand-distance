# mahjong-hand-distance
Little python library for computing the distance between Riichi Mahjong hands

## TODO

- [X] convert estimate_hand_value output to dictionary
- [X] check all hands that can be reached by changing one tile, etc
- [X] add from_int method to Tile
- [X] make hand_distance work with multiple hands
- [ ] check yaku within neighboring_hands(n)
- [ ] make code more efficient
- [ ] figure out how to change repr_html based on the available window: a hand
      should ideally fill the width of the viewport (same with Draw/Discard of
      HandDiff), and Hands should only show several?
- [ ] add classes to tile, hand, hands, handdiff, handsdiff
- [ ] to hand (? hands?), add yaku labels
