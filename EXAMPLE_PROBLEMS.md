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
