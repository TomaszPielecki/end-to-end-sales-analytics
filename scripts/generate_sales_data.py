from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd


SEED = 42
START_DATE = pd.Timestamp("2024-01-01")
END_DATE = pd.Timestamp("2025-12-31")
TARGET_ROWS = 30000
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "sales_data.csv"


@dataclass(frozen=True)
class Product:
    product_id: str
    product_name: str
    category: str
    unit_price: float
    popularity_weight: float


PRODUCT_CATALOG: List[Product] = [
    Product("P001", "4K Smart TV", "Electronics", 899.0, 1.3),
    Product("P002", "Wireless Earbuds", "Electronics", 129.0, 1.9),
    Product("P003", "Gaming Laptop", "Electronics", 1499.0, 0.8),
    Product("P004", "Bluetooth Speaker", "Electronics", 179.0, 1.2),
    Product("P005", "Smartwatch", "Electronics", 249.0, 1.5),
    Product("P006", "Winter Jacket", "Clothing", 139.0, 1.4),
    Product("P007", "Running Shoes", "Clothing", 109.0, 1.8),
    Product("P008", "Denim Jeans", "Clothing", 69.0, 1.6),
    Product("P009", "Classic T-Shirt", "Clothing", 29.0, 2.1),
    Product("P010", "Yoga Leggings", "Clothing", 49.0, 1.7),
    Product("P011", "Air Fryer", "Home", 159.0, 1.5),
    Product("P012", "Coffee Maker", "Home", 119.0, 1.4),
    Product("P013", "Robot Vacuum", "Home", 349.0, 1.0),
    Product("P014", "Desk Lamp", "Home", 45.0, 1.8),
    Product("P015", "Cookware Set", "Home", 199.0, 1.1),
    Product("P016", "Treadmill", "Sports", 799.0, 0.7),
    Product("P017", "Dumbbell Set", "Sports", 89.0, 1.5),
    Product("P018", "Camping Tent", "Sports", 249.0, 1.0),
    Product("P019", "Mountain Bike Helmet", "Sports", 79.0, 1.2),
    Product("P020", "Fitness Tracker", "Sports", 149.0, 1.6),
]


CATEGORY_WEIGHTS: Dict[str, float] = {
    "Electronics": 0.31,
    "Clothing": 0.29,
    "Home": 0.22,
    "Sports": 0.18,
}

REGION_WEIGHTS: Dict[str, float] = {
    "North": 0.30,
    "South": 0.24,
    "East": 0.22,
    "West": 0.24,
}

CHANNEL_BY_REGION: Dict[str, Dict[str, float]] = {
    "North": {"Online": 0.62, "Store": 0.38},
    "South": {"Online": 0.49, "Store": 0.51},
    "East": {"Online": 0.55, "Store": 0.45},
    "West": {"Online": 0.58, "Store": 0.42},
}

CUSTOMER_COUNT = 6000


def build_calendar(start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    calendar = pd.DataFrame({"order_date": dates})
    calendar["month"] = calendar["order_date"].dt.month
    calendar["weekday"] = calendar["order_date"].dt.dayofweek
    calendar["quarter"] = calendar["order_date"].dt.quarter

    base = 1.0
    quarter_multiplier = calendar["quarter"].map({1: 0.92, 2: 0.96, 3: 1.02, 4: 1.32})
    weekday_multiplier = calendar["weekday"].map({0: 1.02, 1: 1.03, 2: 1.00, 3: 1.01, 4: 1.08, 5: 1.15, 6: 0.90})
    month_multiplier = calendar["month"].map(
        {
            1: 0.88,
            2: 0.90,
            3: 0.95,
            4: 0.98,
            5: 1.00,
            6: 1.02,
            7: 1.04,
            8: 1.05,
            9: 1.01,
            10: 1.12,
            11: 1.35,
            12: 1.50,
        }
    )
    promotional_days = np.where(calendar["month"].isin([11, 12]), 1.08, 1.0)
    calendar["daily_weight"] = base * quarter_multiplier * weekday_multiplier * month_multiplier * promotional_days
    calendar["daily_weight"] = calendar["daily_weight"] / calendar["daily_weight"].sum()
    return calendar[["order_date", "daily_weight"]]


def build_product_frame() -> pd.DataFrame:
    frame = pd.DataFrame([product.__dict__ for product in PRODUCT_CATALOG])
    frame["category_weight"] = frame["category"].map(CATEGORY_WEIGHTS)
    frame["product_weight"] = frame["category_weight"] * frame["popularity_weight"]
    return frame


def build_customer_frame(rng: np.random.Generator) -> pd.DataFrame:
    customer_ids = [f"C{customer_id:05d}" for customer_id in range(1, CUSTOMER_COUNT + 1)]
    customer_regions = rng.choice(list(REGION_WEIGHTS.keys()), size=CUSTOMER_COUNT, p=list(REGION_WEIGHTS.values()))
    return pd.DataFrame({"customer_id": customer_ids, "region": customer_regions})


def sample_quantities(rng: np.random.Generator, categories: pd.Series, channels: np.ndarray) -> np.ndarray:
    base_quantity = []
    for category, channel in zip(categories, channels):
        if category == "Electronics":
            lam = 1.15 if channel == "Online" else 1.05
        elif category == "Clothing":
            lam = 2.35 if channel == "Store" else 2.10
        elif category == "Home":
            lam = 1.55
        else:
            lam = 1.45 if channel == "Store" else 1.30

        quantity = max(1, rng.poisson(lam=lam))
        base_quantity.append(quantity)

    return np.array(base_quantity, dtype=int)


def apply_price_variation(
    rng: np.random.Generator,
    base_prices: pd.Series,
    categories: pd.Series,
    order_dates: pd.Series,
) -> np.ndarray:
    variation = rng.normal(loc=1.0, scale=0.06, size=len(base_prices))
    q4_discount = np.where(order_dates.dt.quarter == 4, rng.uniform(0.93, 0.99, size=len(base_prices)), 1.0)
    clothing_spring_boost = np.where(
        (categories == "Clothing") & (order_dates.dt.month.isin([3, 4])),
        rng.uniform(1.01, 1.05, size=len(base_prices)),
        1.0,
    )
    electronics_launch_boost = np.where(
        (categories == "Electronics") & (order_dates.dt.month.isin([9, 10])),
        rng.uniform(1.02, 1.08, size=len(base_prices)),
        1.0,
    )

    prices = base_prices * variation * q4_discount * clothing_spring_boost * electronics_launch_boost
    return np.round(np.clip(prices, a_min=5.0, a_max=None), 2)


def generate_sales_data() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    calendar = build_calendar(START_DATE, END_DATE)
    products = build_product_frame()
    customers = build_customer_frame(rng)

    sampled_dates = rng.choice(calendar["order_date"].to_numpy(), size=TARGET_ROWS, p=calendar["daily_weight"].to_numpy())
    sampled_product_idx = rng.choice(products.index.to_numpy(), size=TARGET_ROWS, p=products["product_weight"] / products["product_weight"].sum())
    sampled_customer_idx = rng.integers(0, CUSTOMER_COUNT, size=TARGET_ROWS)
    sampled_customers = customers.loc[sampled_customer_idx].reset_index(drop=True)
    sampled_regions = sampled_customers["region"].to_numpy()
    sampled_channels = np.array(
        [rng.choice(list(CHANNEL_BY_REGION[region].keys()), p=list(CHANNEL_BY_REGION[region].values())) for region in sampled_regions]
    )

    sales = pd.DataFrame(
        {
            "order_id": [f"O{100000 + i}" for i in range(TARGET_ROWS)],
            "order_date": pd.to_datetime(sampled_dates),
            "customer_id": sampled_customers["customer_id"].to_list(),
            "region": sampled_regions,
            "sales_channel": sampled_channels,
        }
    )

    sales = sales.join(products.loc[sampled_product_idx].reset_index(drop=True))
    sales["quantity"] = sample_quantities(rng, sales["category"], sampled_channels)
    sales["unit_price"] = apply_price_variation(rng, sales["unit_price"], sales["category"], sales["order_date"])
    sales["total_price"] = np.round(sales["quantity"] * sales["unit_price"], 2)
    sales = sales[
        [
            "order_id",
            "order_date",
            "customer_id",
            "product_id",
            "product_name",
            "category",
            "quantity",
            "unit_price",
            "total_price",
            "region",
            "sales_channel",
        ]
    ].sort_values(["order_date", "order_id"], ignore_index=True)

    return sales


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    sales = generate_sales_data()
    sales.to_csv(OUTPUT_PATH, index=False)

    summary = {
        "rows": len(sales),
        "date_min": sales["order_date"].min().date().isoformat(),
        "date_max": sales["order_date"].max().date().isoformat(),
        "revenue": round(float(sales["total_price"].sum()), 2),
        "avg_order_value": round(float(sales["total_price"].mean()), 2),
    }
    print("Generated synthetic sales data:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    print(f"Saved file: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
