#!/bin/sh
# Runs the three shipped examples in order 01 -> 02 -> 03 (lessons carry over), then compares.
# Use --fake for the offline demo:  ./demo.sh --fake
set -e
FAKE=""
if [ "$1" = "--fake" ]; then FAKE="--fake"; fi
hs run $FAKE examples/01_stair_cart.json
hs run $FAKE examples/02_solar_cold_room.json
hs run $FAKE examples/03_footbridge_damping.json
A=$(ls -d runs/*stair-climbing* | tail -1)
B=$(ls -d runs/*off-grid-solar* | tail -1)
C=$(ls -d runs/*vibration-retrofit* | tail -1)
hs compare "$A" "$B" "$C"
