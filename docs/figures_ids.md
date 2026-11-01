# Figure map for path overlays

`docs/figures_map.json` gives the bounding box [x, y, width, height] of every node in
`docs/fig1_architecture.svg` and `docs/fig2_visualization_pipeline.svg` (SVG user units).

To show the path a run took: draw on a copy of the SVG (or its PNG at the same scale), outline the
nodes used in this iteration or round, put numbered step badges on them in time order, draw a thin
arrow between consecutive steps, and fade the rest to about 15% opacity. Save one overlay per Stage A
iteration and per Stage B round. Never edit the figures themselves.
