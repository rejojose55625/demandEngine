# Demand Engine

A retail demand simulation and analytics platform designed to model realistic retail business operations, generate interconnected datasets, and support data-driven analysis and demand forecasting.

## Overview

Demand Engine is a configurable retail business simulator that generates synthetic retail data across stores, products, sales, inventory, suppliers, promotions, competitors and external environmental factors.

Rather than generating isolated sales records, the simulator models the relationships and operational processes behind a retail business. This creates a connected dataset that can be used to explore retail behaviour, analyse business performance, and experiment with demand forecasting techniques.

The simulation incorporates business rules such as product lifecycles, store openings and closures, inventory replenishment, supplier disruptions, promotional activities, competition and seasonal demand patterns.

## Getting Started


### Prerequisites

- Python 3.12+
- Git

### Clone the repository

```bash
git clone https://github.com/RJ-Mechanics/demandEngine.git

cd demandEngine
```

### Create a virtual environment

```bash
python -m venv .venv

source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Generate the datasets

```bash
python run_generation.py
```

Generated datasets are written to the configured output directory.

> Ensure the required configuration parameters and dependencies are available before running the generator.

## License

This project is licensed under the [MIT License](LICENSE).

Copyright (c) 2026 RJ-Mechanics

**Demand Engine** — Simulating retail operations, understanding demand, and building data-driven retail intelligence.
