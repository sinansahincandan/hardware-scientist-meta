# Example problems — fixed demo set

Three mechanical-engineering problems (mechanism, solar thermal-energy system, structural dynamics). They are deliberately **under-constrained**: only the facts that define the problem are given. Everything else (stair geometry, climate and storage temperatures, comfort limits, cost, mass budgets, …) is for the council to establish from literature, standards and datasheets during the meeting (spec §3.1).

Run them in order 01 → 02 → 03 so `lessons.md` carries over.

---

## 01 — Stair-climbing hand truck for parcel couriers

**Intro prompt**
> Couriers in old city centres carry heavy parcels up residential staircases with no lift. Design a hand truck that lets one courier move a load of about 60 kg up and down stairs safely, and that folds into a delivery van.

```json
{
  "title": "Stair-climbing hand truck for parcel couriers",
  "statement": "Couriers in old city centres carry heavy parcels up residential staircases with no lift. Design a hand truck that lets one courier move a load of about 60 kg up and down stairs safely, and that folds into a delivery van.",
  "constraints": [
    "Load about 60 kg",
    "Operated by one person"
  ],
  "criteria": [],
  "attachments": []
}
```

---

## 02 — Off-grid solar-powered cold storage for smallholder farmers

**Intro prompt**
> Smallholder farmers in hot regions without grid electricity lose a large share of their fruit and vegetables after harvest because they cannot keep them cool. Design an energy-efficient, solar-powered cold storage unit that a farming cooperative can use to keep fresh produce cool until it is sold.

```json
{
  "title": "Off-grid solar-powered cold storage for smallholder farmers",
  "statement": "Smallholder farmers in hot regions without grid electricity lose a large share of their fruit and vegetables after harvest because they cannot keep them cool. Design an energy-efficient, solar-powered cold storage unit that a farming cooperative can use to keep fresh produce cool until it is sold.",
  "constraints": [
    "No grid electricity; solar energy only",
    "Store about 1 tonne of fresh produce"
  ],
  "criteria": [],
  "attachments": []
}
```

---

## 03 — Vibration retrofit for a lively pedestrian footbridge

**Intro prompt**
> A 40 m pedestrian footbridge bounces uncomfortably when crowds walk over it. Its first vertical bending mode is about 1.9 Hz with very low damping. Design a retrofit concept that brings the vibration down to a comfortable level without changing how the bridge looks from the deck.

```json
{
  "title": "Vibration retrofit for a lively pedestrian footbridge",
  "statement": "A 40 m pedestrian footbridge bounces uncomfortably when crowds walk over it. Its first vertical bending mode is about 1.9 Hz with very low damping. Design a retrofit concept that brings the vibration down to a comfortable level without changing how the bridge looks from the deck.",
  "constraints": [
    "Span 40 m; first vertical mode about 1.9 Hz"
  ],
  "criteria": [],
  "attachments": []
}
```

---

## 04 — Lunar regolith excavation robot (added round 4, owner-approved 2026-11-03)

Chosen because real solutions are documented: NASA's review of ten years of the Lunabotics Robotic Mining Competition
(Mueller, van Susante, Reiners, Metzger, ASCE Earth & Space 2021,
https://ntrs.nasa.gov/api/citations/20210013143/downloads/ESC2021_Lunabotics_Mueller-PvS_v2_Redacted.pdf) classifies
over 500 student robots by excavation, transport, storage, dumping and mobility mechanism and lists the winners per
year. The constraints below are taken from that review's competition summary. The reference is for comparing the
council's result afterwards; it is never given to the system.

```json
{
  "title": "Lunar regolith excavation robot",
  "statement": "Future lunar bases need loose surface soil (regolith) for building and for extracting oxygen. Design a small robot that drives over a bed of lunar soil simulant, digs it up, carries it and dumps it into a collection bin, operated remotely or autonomously by a team that cannot see or hear the robot.",
  "constraints": [
    "Robot mass at most 60 kg",
    "Fits within 1.0 m long, 0.5 m wide and 0.5 m high at the start",
    "Digs Black Point 1 (BP-1) lunar basalt regolith simulant",
    "Controlled remotely or autonomously, with the operators out of sight and hearing of the robot"
  ],
  "criteria": [],
  "attachments": []
}
```
