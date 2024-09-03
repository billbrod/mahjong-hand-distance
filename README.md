# mahjong-hand-distance
Little python library for computing the distance between Riichi Mahjong hands

## TODO

- [X] convert estimate_hand_value output to dictionary
- [X] check all hands that can be reached by changing one tile, etc
- [X] add from_int method to Tile
- [X] make hand_distance work with multiple hands
- [ ] check yaku within neighboring_hands(n)
- [ ] make code more efficient
      - is it possible to vectorize the neighboring hands? create a 3d array
        where each 2d slice contains a single 1, for each tile, then use
        poss_draw/discards to throw away the impossible ones, then take some
        product to get 1/-1 and add that to the hand?
      - then initialize hands from that?
      - [ ] Vmap hand initialization over first dimension?
      - [X] Remove the any call, just use unique and then drop the all zeros
            afterwards
- [ ] figure out how to change repr_html based on the available window: a hand
      should ideally fill the width of the viewport (same with Draw/Discard of
      HandDiff), and Hands should only show several?
- [ ] add classes to tile, hand, hands, handdiff, handsdiff
- [ ] to hand (? hands?), add yaku labels
