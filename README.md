# Automated Planning for the Dial-a-Ride Problem

## Project Overview

PDDL models for pickup-and-delivery routing, with a Python reference solver, an independent exact oracle and plan validation.

## Problem Statement

Assign and sequence known requests while respecting pickup/dropoff precedence and heterogeneous vehicle capacity. The main cost model minimizes total travel, not action count.

## Technologies Used

PDDL/STRIPS, numeric action costs, durative PDDL, Python standard library; optional Pyperplan 2.1. External planner commands are supplied separately.

## Methodology

Separate declarative models and synthetic instances from the reference search. Compare BFS/UCS/A*/GBFS and independently certify route costs using subset dynamic programming and request partitioning. Replay generated plans to check location, precedence, seats and cost.

## Architecture / Algorithms

Three domain files: STRIPS with seat objects, classical action-cost model, and a temporal model with availability and timed initial literals. Four synthetic sizes range from 1 vehicle/1 request to 3 vehicles/8 requests.

## Experimental Setup

Recorded reference benchmark uses a 5-second search limit. Optimal costs are 7,17,11,48. Four stored oracle plans were replayed during preparation, and the exact oracle reproduced those costs. Pyperplan solved the medium STRIPS instance during this audit (11 actions); no VAL binary was available.

## Results and Evaluation

| Instance | Certified travel cost | Validated plan actions |
|---|---:|---:|
| Easy | 7 | 4 |
| Medium | 17 | 11 |
| Hard | 11 | 18 |
| Very hard | 48 | 30 |

The recorded A* reference result reaches costs 17 and 11 on medium/hard. The very-hard reference search times out at 5 seconds; the oracle still establishes cost 48. [Recorded benchmark](benchmark/results_v2.csv) and [oracle results](benchmark/exact_oracle_results.csv) are separate evidence sources.

## Installation and Usage

Core scripts use only Python's standard library:

```bash
cd benchmark
python exact_oracle.py
python validate_oracle_plans.py
python benchmark_solver_v2.py
```

Optional STRIPS planner, from the repository root:

```bash
pip install -r requirements-planner.txt
python -m pyperplan -H hff -s gbf pddl/darp-strips.pddl pddl/medium-strips.pddl
```

`run_external_planners.sh` contains optional external commands; their logs must be inspected because the original script continues after failures.

## Limitations and Future Improvements

Fast Downward, OPTIC and VAL are integration targets, not demonstrated benchmark results. The temporal model was inspected but not solved with OPTIC. Partial service, latest-pickup windows and accessibility constraints are proposed, not implemented. The oracle certifies the supplied synthetic cost problem, not a municipality-scale transport service.

## Academic Context and Credits

UFSC Artificial Intelligence, Prof. Jomi F. Hübner; DARP teaching scenario introduced by Marco Aurélio Santos de Souza. Submission by Kauan Abegg. Course handouts are excluded. The reference solver, PDDL, oracle and validator are preserved as academic AI-assisted artifacts. The Pyperplan option was corrected from `gbfs` to the installed CLI's `gbf`; no planning algorithm was changed.

See [academic context](ACADEMIC_CONTEXT.md) and [publication review notes](PUBLICATION_NOTES.md).
