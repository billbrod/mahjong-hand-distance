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

Links:
- [ipython notebook output cell truncated](https://stackoverflow.com/questions/23388810/ipython-notebook-output-cell-is-truncating-contents-of-my-list)
- [ellipsis in jupyter notebook output](https://duckduckgo.com/?q=numpy+jupyter+notebook+output+ellipses&t=newext&atb=v350-1&ia=web)
- [docs for mahjong python package](https://github.com/MahjongRepository/mahjong/wiki/English)
- [how to set exports](https://learn.scientific-python.org/development/patterns/exports/#setting-all)
- [pyodide](https://pyodide.org/en/stable/usage/webworker.html)
- ipython
      - [repr html and svg](https://github.com/jupyterlab/jupyterlab/issues/5589)
      - [ipython rich display](https://ipython.readthedocs.io/en/stable/config/integrating.html)
      - [how pandas truncates column display](https://stackoverflow.com/questions/45043968/pandas-display-truncate-column-display-rather-than-wrapping)
- [mahjong hands](https://en.wikipedia.org/wiki/Japanese_mahjong_yaku)
- [mahjong wiki](https://riichi.wiki/Jihai)
- [ruff rules](https://docs.astral.sh/ruff/rules/unnecessary-comprehension-in-call/)
