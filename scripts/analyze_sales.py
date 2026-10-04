from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

try:
    import matplotlib.pyplot as plt
    import seaborn as sns

    HAS_MATPLOTLIB = True
except ModuleNotFoundError:
    HAS_MATPLOTLIB = False


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "sales_data.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"
SUMMARY_PATH = OUTPUT_DIR / "analysis_summary.csv"


def load_sales_data(path: Path) -> pd.DataFrame:
    sales = pd.read_csv(path, parse_dates=["order_date"])
    sales["year_month"] = sales["order_date"].dt.to_period("M").astype(str)
    return sales


def monthly_revenue_trend(sales: pd.DataFrame) -> pd.DataFrame:
    return (
        sales.groupby("year_month", as_index=False)["total_price"]
        .sum()
        .rename(columns={"total_price": "monthly_revenue"})
    )


def top_products(sales: pd.DataFrame) -> pd.DataFrame:
    return (
        sales.groupby(["product_id", "product_name"], as_index=False)
        .agg(total_revenue=("total_price", "sum"), total_quantity=("quantity", "sum"), orders=("order_id", "count"))
        .sort_values("total_revenue", ascending=False)
        .head(10)
    )


def category_revenue(sales: pd.DataFrame) -> pd.DataFrame:
    return (
        sales.groupby("category", as_index=False)
        .agg(total_revenue=("total_price", "sum"), orders=("order_id", "count"))
        .sort_values("total_revenue", ascending=False)
    )


def region_revenue(sales: pd.DataFrame) -> pd.DataFrame:
    return (
        sales.groupby("region", as_index=False)
        .agg(total_revenue=("total_price", "sum"), orders=("order_id", "count"))
        .sort_values("total_revenue", ascending=False)
    )


def sales_channel_comparison(sales: pd.DataFrame) -> pd.DataFrame:
    channel_summary = (
        sales.groupby("sales_channel", as_index=False)
        .agg(total_revenue=("total_price", "sum"), orders=("order_id", "count"))
        .sort_values("total_revenue", ascending=False)
    )
    channel_summary["average_order_value"] = channel_summary["total_revenue"] / channel_summary["orders"]
    return channel_summary


def build_kpis(sales: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("Total Revenue", sales["total_price"].sum()),
            ("Orders", sales["order_id"].nunique()),
            ("Average Order Value", sales["total_price"].mean()),
            ("Unique Customers", sales["customer_id"].nunique()),
            ("Units Sold", sales["quantity"].sum()),
        ],
        columns=["metric", "value"],
    )


def save_summary_tables(
    monthly: pd.DataFrame,
    products: pd.DataFrame,
    category: pd.DataFrame,
    region: pd.DataFrame,
    channels: pd.DataFrame,
    kpis: pd.DataFrame,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    monthly.to_csv(OUTPUT_DIR / "monthly_revenue.csv", index=False)
    products.to_csv(OUTPUT_DIR / "top_10_products.csv", index=False)
    category.to_csv(OUTPUT_DIR / "revenue_by_category.csv", index=False)
    region.to_csv(OUTPUT_DIR / "revenue_by_region.csv", index=False)
    channels.to_csv(OUTPUT_DIR / "sales_channel_comparison.csv", index=False)
    kpis.to_csv(OUTPUT_DIR / "kpis.csv", index=False)

    combined = pd.concat(
        [
            monthly.assign(summary_type="monthly_revenue"),
            products.assign(summary_type="top_products"),
            category.assign(summary_type="category_revenue"),
            region.assign(summary_type="region_revenue"),
            channels.assign(summary_type="channel_comparison"),
            kpis.assign(summary_type="kpi"),
        ],
        ignore_index=True,
        sort=False,
    )
    combined.to_csv(SUMMARY_PATH, index=False)


def ensure_output_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def create_visualizations(
    monthly: pd.DataFrame,
    category: pd.DataFrame,
    region: pd.DataFrame,
    channels: pd.DataFrame,
    products: pd.DataFrame,
    show: bool = False,
) -> None:
    ensure_output_dirs()
    if HAS_MATPLOTLIB:
        try:
            sns.set_theme(style="whitegrid", palette="deep")

            fig, axes = plt.subplots(3, 2, figsize=(18, 16))
            axes = axes.flatten()

            sns.lineplot(data=monthly, x="year_month", y="monthly_revenue", marker="o", ax=axes[0])
            axes[0].set_title("Monthly Revenue Trend")
            axes[0].tick_params(axis="x", rotation=45)
            axes[0].set_xlabel("Month")
            axes[0].set_ylabel("Revenue")

            sns.barplot(data=category, x="category", y="total_revenue", ax=axes[1])
            axes[1].set_title("Revenue by Category")
            axes[1].set_xlabel("Category")
            axes[1].set_ylabel("Revenue")

            sns.barplot(data=region, x="region", y="total_revenue", ax=axes[2])
            axes[2].set_title("Revenue by Region")
            axes[2].set_xlabel("Region")
            axes[2].set_ylabel("Revenue")

            sns.barplot(data=channels, x="sales_channel", y="total_revenue", ax=axes[3])
            axes[3].set_title("Revenue by Sales Channel")
            axes[3].set_xlabel("Channel")
            axes[3].set_ylabel("Revenue")

            sns.barplot(data=products, x="total_revenue", y="product_name", ax=axes[4])
            axes[4].set_title("Top 10 Products by Revenue")
            axes[4].set_xlabel("Revenue")
            axes[4].set_ylabel("Product")

            axes[5].axis("off")
            axes[5].text(
                0.0,
                0.9,
                "\n".join(
                    [
                        "Core Metrics",
                        f"Total Revenue: ${monthly['monthly_revenue'].sum():,.0f}",
                        f"Orders: {int(channels['orders'].sum()):,}",
                        f"Average Order Value: ${monthly['monthly_revenue'].sum() / channels['orders'].sum():.2f}",
                    ]
                ),
                fontsize=14,
                va="top",
            )

            plt.tight_layout()
            plt.savefig(OUTPUT_DIR / "sales_analysis_dashboard.png", dpi=200, bbox_inches="tight")
            if show:
                plt.show()
            plt.close(fig)
            return
        except Exception:  # noqa: BLE001
            # Fall back when local matplotlib/seaborn/pandas versions are incompatible.
            pass

    create_pil_dashboard(monthly, category, region, channels, products, show=show)


def create_portfolio_screenshots(
    monthly: pd.DataFrame,
    category: pd.DataFrame,
    region: pd.DataFrame,
    channels: pd.DataFrame,
    products: pd.DataFrame,
    kpis: pd.DataFrame,
) -> None:
    ensure_output_dirs()
    create_kpi_snapshot(kpis, products, category, SCREENSHOT_DIR / "01_kpi_overview.png")
    create_line_snapshot(
        title="Monthly Revenue Trend",
        subtitle="Seasonality across 24 months",
        labels=monthly["year_month"].tolist(),
        values=monthly["monthly_revenue"].tolist(),
        output_path=SCREENSHOT_DIR / "02_monthly_revenue_trend.png",
        accent="#2563eb",
    )
    create_bar_snapshot(
        title="Revenue by Category",
        subtitle="Category contribution to total revenue",
        labels=category["category"].tolist(),
        values=category["total_revenue"].tolist(),
        output_path=SCREENSHOT_DIR / "03_revenue_by_category.png",
        accent="#0ea5e9",
    )
    create_bar_snapshot(
        title="Revenue by Region",
        subtitle="Regional performance comparison",
        labels=region["region"].tolist(),
        values=region["total_revenue"].tolist(),
        output_path=SCREENSHOT_DIR / "04_revenue_by_region.png",
        accent="#10b981",
    )
    create_bar_snapshot(
        title="Sales Channel Comparison",
        subtitle="Online vs Store revenue",
        labels=channels["sales_channel"].tolist(),
        values=channels["total_revenue"].tolist(),
        output_path=SCREENSHOT_DIR / "05_sales_channel_comparison.png",
        accent="#f59e0b",
    )
    create_bar_snapshot(
        title="Top Products by Revenue",
        subtitle="Highest-value products in the portfolio",
        labels=products.head(5)["product_name"].tolist(),
        values=products.head(5)["total_revenue"].tolist(),
        output_path=SCREENSHOT_DIR / "06_top_products.png",
        accent="#8b5cf6",
        horizontal=True,
    )


def draw_bar_chart(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    height: int,
    title: str,
    labels: list[str],
    values: list[float],
    color: str,
    font: ImageFont.ImageFont,
) -> None:
    draw.text((x, y), title, fill="#1f2937", font=font)
    chart_top = y + 30
    chart_bottom = y + height - 30
    chart_left = x + 90
    chart_right = x + width - 20
    draw.rectangle((chart_left, chart_top, chart_right, chart_bottom), outline="#cbd5e1", width=1)

    max_value = max(values) if values else 1
    row_height = (chart_bottom - chart_top) / max(len(values), 1)

    for index, (label, value) in enumerate(zip(labels, values)):
        bar_y1 = chart_top + index * row_height + 8
        bar_y2 = bar_y1 + row_height - 12
        bar_width = 0 if max_value == 0 else (value / max_value) * (chart_right - chart_left - 10)
        draw.text((x, bar_y1), str(label), fill="#334155", font=font)
        draw.rectangle((chart_left + 2, bar_y1, chart_left + 2 + bar_width, bar_y2), fill=color)
        draw.text((chart_left + 8 + bar_width, bar_y1), f"${value:,.0f}", fill="#475569", font=font)


def draw_line_chart(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    height: int,
    title: str,
    labels: list[str],
    values: list[float],
    font: ImageFont.ImageFont,
) -> None:
    draw.text((x, y), title, fill="#1f2937", font=font)
    chart_top = y + 30
    chart_bottom = y + height - 40
    chart_left = x + 50
    chart_right = x + width - 20
    draw.rectangle((chart_left, chart_top, chart_right, chart_bottom), outline="#cbd5e1", width=1)

    max_value = max(values) if values else 1
    min_value = min(values) if values else 0
    span = max(max_value - min_value, 1)
    points = []

    for index, value in enumerate(values):
        px = chart_left + index * ((chart_right - chart_left) / max(len(values) - 1, 1))
        py = chart_bottom - ((value - min_value) / span) * (chart_bottom - chart_top)
        points.append((px, py))

    if len(points) > 1:
        draw.line(points, fill="#2563eb", width=3)
    for px, py in points:
        draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill="#1d4ed8")

    tick_positions = list(range(0, len(labels), max(len(labels) // 6, 1)))
    for tick in tick_positions:
        draw.text((chart_left + tick * ((chart_right - chart_left) / max(len(labels) - 1, 1)) - 15, chart_bottom + 8), labels[tick], fill="#475569", font=font)


def create_pil_dashboard(
    monthly: pd.DataFrame,
    category: pd.DataFrame,
    region: pd.DataFrame,
    channels: pd.DataFrame,
    products: pd.DataFrame,
    show: bool = False,
) -> None:
    width, height = 1800, 1400
    canvas = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.load_default()
    body_font = ImageFont.load_default()

    draw.text((40, 20), "Sales Analysis Dashboard", fill="#0f172a", font=title_font)
    draw.text((40, 50), "Fallback visualization rendered with Pillow because matplotlib/seaborn is not installed.", fill="#64748b", font=body_font)

    draw_line_chart(
        draw,
        x=40,
        y=100,
        width=1720,
        height=300,
        title="Monthly Revenue Trend",
        labels=monthly["year_month"].tolist(),
        values=monthly["monthly_revenue"].tolist(),
        font=body_font,
    )

    draw_bar_chart(
        draw,
        x=40,
        y=450,
        width=830,
        height=300,
        title="Revenue by Category",
        labels=category["category"].tolist(),
        values=category["total_revenue"].tolist(),
        color="#0ea5e9",
        font=body_font,
    )

    draw_bar_chart(
        draw,
        x=930,
        y=450,
        width=830,
        height=300,
        title="Revenue by Region",
        labels=region["region"].tolist(),
        values=region["total_revenue"].tolist(),
        color="#10b981",
        font=body_font,
    )

    draw_bar_chart(
        draw,
        x=40,
        y=800,
        width=830,
        height=220,
        title="Revenue by Sales Channel",
        labels=channels["sales_channel"].tolist(),
        values=channels["total_revenue"].tolist(),
        color="#f59e0b",
        font=body_font,
    )

    top_products = products.head(5)
    draw_bar_chart(
        draw,
        x=930,
        y=800,
        width=830,
        height=220,
        title="Top 5 Products by Revenue",
        labels=top_products["product_name"].tolist(),
        values=top_products["total_revenue"].tolist(),
        color="#8b5cf6",
        font=body_font,
    )

    metrics_y = 1080
    draw.text((40, metrics_y), "Core Metrics", fill="#0f172a", font=title_font)
    metrics = [
        f"Total Revenue: ${monthly['monthly_revenue'].sum():,.0f}",
        f"Orders: {int(channels['orders'].sum()):,}",
        f"Average Order Value: ${monthly['monthly_revenue'].sum() / channels['orders'].sum():.2f}",
        f"Best Category: {category.iloc[0]['category']}",
        f"Top Product: {products.iloc[0]['product_name']}",
    ]
    for index, metric in enumerate(metrics):
        draw.text((40, metrics_y + 35 + index * 28), metric, fill="#334155", font=body_font)

    output_file = OUTPUT_DIR / "sales_analysis_dashboard.png"
    canvas.save(output_file)
    if show:
        canvas.show()


def create_kpi_snapshot(
    kpis: pd.DataFrame,
    products: pd.DataFrame,
    category: pd.DataFrame,
    output_path: Path,
) -> None:
    canvas = Image.new("RGB", (1500, 850), color="#f8fafc")
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.load_default()
    body_font = ImageFont.load_default()

    draw.text((40, 30), "KPI Overview", fill="#0f172a", font=title_font)
    draw.text((40, 55), "Executive snapshot of the synthetic sales project", fill="#475569", font=body_font)

    card_positions = [(40, 120), (390, 120), (740, 120), (1090, 120), (40, 340)]
    kpi_items = list(kpis.itertuples(index=False))
    for (x, y), item in zip(card_positions, kpi_items):
        draw.rounded_rectangle((x, y, x + 300, y + 160), radius=18, fill="white", outline="#cbd5e1", width=2)
        draw.text((x + 20, y + 20), item.metric, fill="#334155", font=body_font)
        value = item.value
        if item.metric in {"Total Revenue", "Average Order Value"}:
            value_text = f"${value:,.2f}"
        else:
            value_text = f"{int(value):,}"
        draw.text((x + 20, y + 75), value_text, fill="#0f172a", font=title_font)

    draw.rounded_rectangle((390, 340, 1390, 760), radius=18, fill="white", outline="#cbd5e1", width=2)
    draw.text((420, 370), "Headline Findings", fill="#0f172a", font=title_font)
    findings = [
        f"Top category: {category.iloc[0]['category']} (${category.iloc[0]['total_revenue']:,.0f})",
        f"Top product: {products.iloc[0]['product_name']} (${products.iloc[0]['total_revenue']:,.0f})",
        f"Second-best product: {products.iloc[1]['product_name']} (${products.iloc[1]['total_revenue']:,.0f})",
        "Dataset includes 2 years of daily sales with built-in seasonality and channel mix.",
    ]
    for index, finding in enumerate(findings):
        draw.text((420, 420 + index * 55), f"- {finding}", fill="#334155", font=body_font)

    canvas.save(output_path)


def create_line_snapshot(
    title: str,
    subtitle: str,
    labels: list[str],
    values: list[float],
    output_path: Path,
    accent: str,
) -> None:
    canvas = Image.new("RGB", (1500, 900), color="white")
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.load_default()
    body_font = ImageFont.load_default()
    draw.text((40, 25), title, fill="#0f172a", font=title_font)
    draw.text((40, 50), subtitle, fill="#64748b", font=body_font)

    chart_top, chart_left, chart_bottom, chart_right = 120, 80, 760, 1440
    draw.rectangle((chart_left, chart_top, chart_right, chart_bottom), outline="#cbd5e1", width=2)

    max_value = max(values) if values else 1
    min_value = min(values) if values else 0
    span = max(max_value - min_value, 1)
    points = []
    for index, value in enumerate(values):
        px = chart_left + index * ((chart_right - chart_left) / max(len(values) - 1, 1))
        py = chart_bottom - ((value - min_value) / span) * (chart_bottom - chart_top - 30) - 15
        points.append((px, py))

    if len(points) > 1:
        draw.line(points, fill=accent, width=4)
    for px, py in points:
        draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill=accent)

    for tick in range(5):
        tick_value = min_value + (span * tick / 4)
        y = chart_bottom - ((tick_value - min_value) / span) * (chart_bottom - chart_top - 30) - 15
        draw.line((chart_left, y, chart_right, y), fill="#e2e8f0", width=1)
        draw.text((15, y - 5), f"${tick_value/1000:,.0f}k", fill="#64748b", font=body_font)

    tick_positions = list(range(0, len(labels), max(len(labels) // 6, 1)))
    if tick_positions[-1] != len(labels) - 1:
        tick_positions.append(len(labels) - 1)
    for tick in tick_positions:
        x = chart_left + tick * ((chart_right - chart_left) / max(len(labels) - 1, 1))
        draw.text((x - 25, chart_bottom + 12), labels[tick], fill="#64748b", font=body_font)

    canvas.save(output_path)


def create_bar_snapshot(
    title: str,
    subtitle: str,
    labels: list[str],
    values: list[float],
    output_path: Path,
    accent: str,
    horizontal: bool = False,
) -> None:
    canvas = Image.new("RGB", (1500, 900), color="white")
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.load_default()
    body_font = ImageFont.load_default()
    draw.text((40, 25), title, fill="#0f172a", font=title_font)
    draw.text((40, 50), subtitle, fill="#64748b", font=body_font)

    if horizontal:
        draw_bar_chart(
            draw,
            x=40,
            y=110,
            width=1420,
            height=700,
            title="",
            labels=labels,
            values=values,
            color=accent,
            font=body_font,
        )
    else:
        chart_top, chart_left, chart_bottom, chart_right = 120, 90, 760, 1440
        draw.rectangle((chart_left, chart_top, chart_right, chart_bottom), outline="#cbd5e1", width=2)
        max_value = max(values) if values else 1
        bar_width = (chart_right - chart_left) / max(len(values), 1) * 0.55

        for index, (label, value) in enumerate(zip(labels, values)):
            x_center = chart_left + (index + 0.5) * ((chart_right - chart_left) / max(len(values), 1))
            bar_height = 0 if max_value == 0 else (value / max_value) * (chart_bottom - chart_top - 60)
            x1 = x_center - bar_width / 2
            x2 = x_center + bar_width / 2
            y1 = chart_bottom - bar_height
            draw.rectangle((x1, y1, x2, chart_bottom), fill=accent)
            draw.text((x_center - 30, chart_bottom + 12), str(label), fill="#64748b", font=body_font)
            draw.text((x_center - 38, y1 - 18), f"${value/1000:,.0f}k", fill="#334155", font=body_font)

        for tick in range(5):
            tick_value = max_value * tick / 4
            y = chart_bottom - (tick_value / max_value) * (chart_bottom - chart_top - 60) if max_value else chart_bottom
            draw.line((chart_left, y, chart_right, y), fill="#e2e8f0", width=1)
            draw.text((20, y - 5), f"${tick_value/1000:,.0f}k", fill="#64748b", font=body_font)

    canvas.save(output_path)


def print_console_summary(
    kpis: pd.DataFrame,
    category: pd.DataFrame,
    region: pd.DataFrame,
    channels: pd.DataFrame,
    products: pd.DataFrame,
) -> None:
    kpi_lookup = dict(zip(kpis["metric"], kpis["value"]))
    top_category = category.iloc[0]
    weakest_region = region.iloc[-1]
    top_product = products.iloc[0]

    print("\n=== SALES SUMMARY ===")
    print(f"Total Revenue       : ${kpi_lookup['Total Revenue']:,.2f}")
    print(f"Total Orders        : {int(kpi_lookup['Orders']):,}")
    print(f"Average Order Value : ${kpi_lookup['Average Order Value']:,.2f}")
    print(f"Unique Customers    : {int(kpi_lookup['Unique Customers']):,}")
    print(f"Units Sold          : {int(kpi_lookup['Units Sold']):,}")

    print("\n=== QUICK INSIGHTS ===")
    print(f"Top category        : {top_category['category']} (${top_category['total_revenue']:,.2f})")
    print(f"Weakest region      : {weakest_region['region']} (${weakest_region['total_revenue']:,.2f})")
    print(f"Top product         : {top_product['product_name']} (${top_product['total_revenue']:,.2f})")

    print("\n=== CHANNEL PERFORMANCE ===")
    for row in channels.itertuples(index=False):
        print(f"{row.sales_channel:<18} Revenue=${row.total_revenue:,.2f}  Orders={int(row.orders):,}  AOV=${row.average_order_value:,.2f}")

    print("\n=== TOP 5 PRODUCTS ===")
    for row in products.head(5).itertuples(index=False):
        print(f"{row.product_name:<20} Revenue=${row.total_revenue:,.2f}  Orders={int(row.orders):,}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze synthetic sales data and build a local report.")
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the dashboard window after generating outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sales = load_sales_data(DATA_PATH)

    monthly = monthly_revenue_trend(sales)
    products = top_products(sales)
    category = category_revenue(sales)
    region = region_revenue(sales)
    channels = sales_channel_comparison(sales)
    kpis = build_kpis(sales)

    save_summary_tables(monthly, products, category, region, channels, kpis)
    create_visualizations(monthly, category, region, channels, products, show=args.show)
    create_portfolio_screenshots(monthly, category, region, channels, products, kpis)
    print_console_summary(kpis, category, region, channels, products)

    print("Analysis complete.")
    print(f"Source data: {DATA_PATH}")
    print(f"Outputs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
