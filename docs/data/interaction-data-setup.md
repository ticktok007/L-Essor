# Interaction Data Setup
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 1 — Synthetic Data Foundation

## Required Packages
- `Faker` — synthetic names, dates, and context text
- `matplotlib` — degree distribution sanity plot

## Install Command
```bash
pip install faker matplotlib
```

## Purpose
Generates the interaction edge table (graph backbone for NetworkX SNA),
competition participation records, achievement records, and a degree-distribution
plot confirming the graph is realistic (hub-and-spoke, not uniform random).