"""
Data Generator - Synthetic Dataset Creation

This module generates synthetic car sales data for demonstration purposes.
Can be replaced with real data loading functionality.

Author: [Your Name]
"""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def make_car_sales_df(n_rows: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Generate the synthetic car sales dataset from the notebook."""
    rng = np.random.default_rng(seed)

    start_date = datetime(2022, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_rows)]

    makes = [
        "Toyota",
        "Honda",
        "Ford",
        "Chevrolet",
        "Nissan",
        "BMW",
        "Mercedes",
        "Audi",
        "Hyundai",
        "Kia",
    ]
    models = ["Sedan", "SUV", "Truck", "Hatchback", "Coupe", "Van"]
    colors = ["Red", "Blue", "Black", "White", "Silver", "Gray", "Green"]
    sales_people = ["Alice", "Bob", "Charlie", "David", "Eva"]

    data = {
        "Date": dates,
        "Make": rng.choice(makes, n_rows),
        "Model": rng.choice(models, n_rows),
        "Color": rng.choice(colors, n_rows),
        "Year": rng.integers(2015, 2023, n_rows),
        "Price": rng.uniform(20000, 80000, n_rows).round(2),
        "Mileage": rng.uniform(0, 100000, n_rows).round(0),
        "EngineSize": rng.choice([1.6, 2.0, 2.5, 3.0, 3.5, 4.0], n_rows),
        "FuelEfficiency": rng.uniform(20, 40, n_rows).round(1),
        "SalesPerson": rng.choice(sales_people, n_rows),
    }

    return pd.DataFrame(data).sort_values("Date")

