"""
Generates: topic18_analysis_grouping.ipynb
Run: python build_topic18_notebook.py
"""

import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

cells = []

# ─────────────────────────────────────────────
# TITLE
# ─────────────────────────────────────────────
cells.append(new_markdown_cell("""\
# 📊 Topic 18 — Basic Data Analysis & Grouping
### Week 3 · IT for Youth Ghana · Data Analytics with Python

---

**How to use this notebook**
- Run cells top to bottom — **Shift + Enter**
- **🔨 Try It** cells are yours to complete
- **⚡ Live Coding** cells — follow along with the instructor

> 📁 **Before you start:** Upload `regional_sales_1000.csv` to Colab
"""))

# ─────────────────────────────────────────────
# INTRO
# ─────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## 🎯 From Cleaning to Answers

In Topic 17 you cleaned messy data. Now you have a dataset
that is accurate, consistent, and ready for the real work —
**answering business questions**.

This topic teaches the analytical toolkit that sits between
a clean DataFrame and a meaningful insight:

| Tool | What it answers |
|------|----------------|
| `.sort_values()` | What is the ranking? |
| Filtering + `.agg()` | What is the summary for this group? |
| `.groupby()` | How does this vary across categories? |
| `.agg()` with multiple functions | What are all the stats per group? |
| `pd.crosstab()` | How do two categories relate? |
| `.to_csv()` | How do I share these results? |

We will work through all of these using 1,000 sales records
from six regions of Ghana — and produce our first complete
analytical report by the end.
"""))

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## 📂 Stage 1 — Load & Verify the Data
"""))

cells.append(new_code_cell("""\
import pandas as pd
import numpy as np

df = pd.read_csv("regional_sales_1000.csv", parse_dates=["date"])

print(f"Shape  : {df.shape}")
print(f"Columns: {list(df.columns)}")
print()
print(df.head(6))
"""))

cells.append(new_code_cell("""\
# Quick data health check
print("Missing values:")
print(df.isnull().sum())
print()
print("Data types:")
print(df.dtypes)
print()
print("Date range:")
print(f"  {df['date'].min().date()}  →  {df['date'].max().date()}")
print()
print("Unique values:")
for col in ["region","product_category","quarter","channel"]:
    print(f"  {col:<20} : {sorted(df[col].unique())}")
"""))

# ─────────────────────────────────────────────
# PART 1 — SORT VALUES
# ─────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## 🔢 Part 1 — Sorting with .sort_values()

Sorting answers the question: **"What is the ranking?"**
"""))

cells.append(new_code_cell("""\
# ── Top 10 sales by total revenue ───────────────────────────
top10 = df.sort_values("total_revenue_ghs", ascending=False).head(10)
print("TOP 10 INDIVIDUAL SALES BY REVENUE:")
print(top10[["sale_id","region","product_category","product_name",
             "units_sold","total_revenue_ghs"]].to_string(index=False))
"""))

cells.append(new_code_cell("""\
# ── Sort by multiple columns ──────────────────────────────────
# Region A→Z, then revenue high→low within each region
multi = df.sort_values(
    ["region","total_revenue_ghs"],
    ascending=[True, False]
)
print("First 10 rows sorted by region then revenue:")
print(multi[["region","product_category","total_revenue_ghs"]].head(10).to_string(index=False))
"""))

cells.append(new_markdown_cell("""\
**🔨 Try It 1** — Find the top 5 sales reps by their single highest sale.  
Which sales rep made the biggest individual transaction?
"""))

cells.append(new_code_cell("""\
# 🔨 TRY IT 1
# Hint: sort by total_revenue_ghs descending, then look at sales_rep column
# YOUR CODE HERE
"""))

# ─────────────────────────────────────────────
# PART 2 — GROUPBY BASICS
# ─────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## 🗂️ Part 2 — The .groupby() Method

`.groupby()` is the most powerful tool in pandas for answering
analytical questions. It splits your DataFrame into groups,
applies a function to each group, and combines the results.

**Split → Apply → Combine**
"""))

cells.append(new_code_cell("""\
# ── groupby with a single aggregation ───────────────────────

# Total revenue per region
region_revenue = df.groupby("region")["total_revenue_ghs"].sum()
print("Total revenue by region:")
print(region_revenue.sort_values(ascending=False))
print()
print(f"Top region: {region_revenue.idxmax()}  "
      f"GH₵ {region_revenue.max():,.2f}")
"""))

cells.append(new_code_cell("""\
# ── Different aggregations on the same group ─────────────────

# Count, mean, max per product category
print("Product category summary:")
cat_summary = df.groupby("product_category")["total_revenue_ghs"].agg(
    total_sales="count",
    avg_revenue="mean",
    max_revenue="max",
    total_revenue="sum"
).round(2).sort_values("total_revenue", ascending=False)

print(cat_summary.to_string())
"""))

cells.append(new_code_cell("""\
# ── Multiple columns in groupby ──────────────────────────────
# Revenue by region AND channel

region_channel = df.groupby(["region","channel"])["total_revenue_ghs"].sum()
region_channel = region_channel.reset_index()
region_channel = region_channel.sort_values(
    ["region","total_revenue_ghs"], ascending=[True,False])

print("Revenue by region and channel:")
print(region_channel.to_string(index=False))
"""))

cells.append(new_markdown_cell("""\
**🔨 Try It 2** — Answer these three questions using `.groupby()`:
1. Which sales rep generated the most total revenue?
2. Which quarter had the highest number of units sold?
3. What is the average revenue per sale for each channel (In-Store / Online / Wholesale)?
"""))

cells.append(new_code_cell("""\
# 🔨 TRY IT 2

# 1. Top sales rep by total revenue
# YOUR CODE HERE

# 2. Quarter with most units sold
# YOUR CODE HERE

# 3. Average revenue per channel
# YOUR CODE HERE
"""))

# ─────────────────────────────────────────────
# PART 3 — AGG WITH MULTIPLE FUNCTIONS
# ─────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## 📐 Part 3 — .agg() with Multiple Functions

When you need more than one stat per group at once,
pass a dictionary to `.agg()` — one aggregation per column.
"""))

cells.append(new_code_cell("""\
# Full sales summary per region
region_full = df.groupby("region").agg(
    total_transactions = ("sale_id",           "count"),
    total_units_sold   = ("units_sold",         "sum"),
    total_revenue      = ("total_revenue_ghs",  "sum"),
    avg_revenue        = ("total_revenue_ghs",  "mean"),
    max_single_sale    = ("total_revenue_ghs",  "max"),
    min_single_sale    = ("total_revenue_ghs",  "min"),
).round(2)

region_full = region_full.sort_values("total_revenue", ascending=False)
print("COMPREHENSIVE REGION SUMMARY:")
print(region_full.to_string())
"""))

cells.append(new_code_cell("""\
# Quarterly trend — how did revenue change across Q1–Q4?
quarterly = df.groupby("quarter").agg(
    transactions = ("sale_id",           "count"),
    total_rev    = ("total_revenue_ghs",  "sum"),
    avg_rev      = ("total_revenue_ghs",  "mean"),
).round(2)

print("QUARTERLY REVENUE TREND:")
print(quarterly.to_string())
print()

# Calculate quarter-on-quarter growth
rev_list = quarterly["total_rev"].tolist()
for i in range(1, len(rev_list)):
    growth = ((rev_list[i] - rev_list[i-1]) / rev_list[i-1]) * 100
    direction = "↑" if growth > 0 else "↓"
    print(f"  Q{i} → Q{i+1}: {direction} {abs(growth):.1f}%")
"""))

cells.append(new_code_cell("""\
# Sales rep performance leaderboard
rep_board = df.groupby("sales_rep").agg(
    deals       = ("sale_id",           "count"),
    total_rev   = ("total_revenue_ghs",  "sum"),
    avg_deal    = ("total_revenue_ghs",  "mean"),
    best_deal   = ("total_revenue_ghs",  "max"),
).round(2).sort_values("total_rev", ascending=False)

print("SALES REP LEADERBOARD:")
print(rep_board.to_string())
"""))

cells.append(new_markdown_cell("""\
**🔨 Try It 3** — Using `.agg()`, build a full summary table
for each product category showing:
- Number of transactions
- Total units sold
- Total revenue
- Average revenue per transaction
- Revenue as a percentage of the overall total

Sort by total revenue descending. Print cleanly formatted.
"""))

cells.append(new_code_cell("""\
# 🔨 TRY IT 3
# YOUR CODE HERE

# Hint for the percentage column:
# After creating the summary, add a new column:
# summary["pct_of_total"] = (summary["total_revenue"] / df["total_revenue_ghs"].sum() * 100).round(1)
"""))

# ─────────────────────────────────────────────
# PART 4 — FILTER + GROUP
# ─────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## 🔍 Part 4 — Filter Then Group

Combine filtering with groupby to answer
more specific analytical questions.
"""))

cells.append(new_code_cell("""\
# ── Online channel analysis ───────────────────────────────────
online = df[df["channel"] == "Online"]

online_by_cat = online.groupby("product_category")["total_revenue_ghs"].agg(
    orders="count",
    total="sum",
    avg="mean"
).round(2).sort_values("total", ascending=False)

print("ONLINE CHANNEL — Revenue by Category:")
print(online_by_cat.to_string())
"""))

cells.append(new_code_cell("""\
# ── High-value transactions only (>GH₵1,000) ─────────────────
high_value = df[df["total_revenue_ghs"] > 1000]

print(f"Transactions above GH₵1,000: {len(high_value)}")
print(f"As % of all transactions   : {len(high_value)/len(df)*100:.1f}%")
print(f"Revenue from these deals   : GH₵ {high_value['total_revenue_ghs'].sum():,.2f}")
print()

by_region = high_value.groupby("region")["total_revenue_ghs"].agg(
    deals="count",
    revenue="sum"
).sort_values("revenue", ascending=False)
print("High-value deals by region:")
print(by_region.to_string())
"""))

cells.append(new_code_cell("""\
# ── Q4 vs Q1 comparison per region ───────────────────────────
q1_rev = df[df["quarter"]=="Q1"].groupby("region")["total_revenue_ghs"].sum()
q4_rev = df[df["quarter"]=="Q4"].groupby("region")["total_revenue_ghs"].sum()

comparison = pd.DataFrame({"Q1": q1_rev, "Q4": q4_rev})
comparison["growth_pct"] = ((comparison["Q4"] - comparison["Q1"])
                             / comparison["Q1"] * 100).round(1)
comparison = comparison.sort_values("growth_pct", ascending=False)

print("Q1 → Q4 REVENUE GROWTH BY REGION:")
print(comparison.to_string())
print()
print(f"Best growth  : {comparison['growth_pct'].idxmax()} "
      f"({comparison['growth_pct'].max()}%)")
print(f"Worst growth : {comparison['growth_pct'].idxmin()} "
      f"({comparison['growth_pct'].min()}%)")
"""))

# ─────────────────────────────────────────────
# PART 5 — CROSSTAB
# ─────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## 🔲 Part 5 — pd.crosstab()

`pd.crosstab()` creates a frequency table that shows how
two categorical variables relate to each other.
Think of it as a pivot table — one category in the rows,
another in the columns, and counts (or aggregated values) in the cells.
"""))

cells.append(new_code_cell("""\
# ── Basic crosstab: region × product_category (count) ────────
ct_count = pd.crosstab(df["region"], df["product_category"])
print("TRANSACTIONS per Region × Category:")
print(ct_count.to_string())
"""))

cells.append(new_code_cell("""\
# ── Crosstab with values (sum of revenue) ────────────────────
ct_revenue = pd.crosstab(
    df["region"],
    df["product_category"],
    values=df["total_revenue_ghs"],
    aggfunc="sum",
).round(0).fillna(0)

print("REVENUE (GH₵) per Region × Category:")
print(ct_revenue.to_string())
print()

# Add row totals and column totals
ct_revenue["TOTAL"] = ct_revenue.sum(axis=1)
ct_revenue.loc["TOTAL"] = ct_revenue.sum()
print("WITH TOTALS:")
print(ct_revenue.to_string())
"""))

cells.append(new_code_cell("""\
# ── Channel × Quarter crosstab ────────────────────────────────
ct_channel_q = pd.crosstab(
    df["channel"],
    df["quarter"],
    values=df["total_revenue_ghs"],
    aggfunc="sum"
).round(2)

print("REVENUE per Channel × Quarter:")
print(ct_channel_q.to_string())
"""))

cells.append(new_markdown_cell("""\
**🔨 Try It 4** — Create a crosstab of `sales_rep` × `channel`
showing the **number of transactions** each rep made per channel.
Then answer: which sales rep is most dominant in the Online channel?
"""))

cells.append(new_code_cell("""\
# 🔨 TRY IT 4
# YOUR CODE HERE
"""))

# ─────────────────────────────────────────────
# PART 6 — FULL PIPELINE
# ─────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## 🏁 Part 6 — Full Analytics Pipeline: Ghana Regional Sales Report

Now we run the complete five-stage pipeline and produce
a formatted report with insights and an exported summary file.
"""))

cells.append(new_markdown_cell("""\
### Stage 1 & 2 — Data is already loaded and clean ✅
"""))

cells.append(new_code_cell("""\
# Confirm the dataset is clean
print(f"Records      : {len(df):,}")
print(f"Date range   : {df['date'].min().date()} → {df['date'].max().date()}")
print(f"Missing vals : {df.isnull().sum().sum()}")
print(f"Total revenue: GH₵ {df['total_revenue_ghs'].sum():,.2f}")
"""))

cells.append(new_markdown_cell("""\
### Stage 3 — EDA
"""))

cells.append(new_code_cell("""\
# Overall revenue distribution
print("REVENUE STATISTICS (per transaction)")
print("-" * 40)
stats = df["total_revenue_ghs"].describe().round(2)
for stat, val in stats.items():
    print(f"  {stat:<8} : GH₵ {val:>10,.2f}")
print()

# Distribution by quarter
print("TRANSACTIONS PER QUARTER:")
q_counts = df["quarter"].value_counts().sort_index()
for q, cnt in q_counts.items():
    bar = "█" * (cnt // 10)
    print(f"  {q}  {cnt:>4} transactions  {bar}")
"""))

cells.append(new_code_cell("""\
# Category mix
print("PRODUCT CATEGORY MIX:")
cat_mix = df.groupby("product_category")["total_revenue_ghs"].sum()
cat_mix_pct = (cat_mix / cat_mix.sum() * 100).round(1)
cat_mix = cat_mix.sort_values(ascending=False)

for cat in cat_mix.index:
    pct = cat_mix_pct[cat]
    bar = "█" * int(pct * 1.5)
    print(f"  {cat:<25} {cat_mix[cat]:>12,.0f} GH₵  {pct:>5}%  {bar}")
"""))

cells.append(new_markdown_cell("""\
### Stage 4 — Analysis
"""))

cells.append(new_code_cell("""\
# ── Key findings ─────────────────────────────────────────────

# 1. Top performing region
region_rev  = df.groupby("region")["total_revenue_ghs"].sum()
top_region  = region_rev.idxmax()
top_rev     = region_rev.max()
total_rev   = region_rev.sum()
top_share   = top_rev / total_rev * 100

# 2. Best product category
cat_rev     = df.groupby("product_category")["total_revenue_ghs"].sum()
top_cat     = cat_rev.idxmax()

# 3. Best quarter
q_rev       = df.groupby("quarter")["total_revenue_ghs"].sum()
top_q       = q_rev.idxmax()
top_q_rev   = q_rev.max()

# 4. MoMo vs other channels? — check channel performance
chan_rev    = df.groupby("channel")["total_revenue_ghs"].sum()
top_channel = chan_rev.idxmax()

# 5. Top sales rep
rep_rev     = df.groupby("sales_rep")["total_revenue_ghs"].sum()
top_rep     = rep_rev.idxmax()
top_rep_rev = rep_rev.max()

# 6. Average revenue per transaction by region
avg_by_region = df.groupby("region")["total_revenue_ghs"].mean()
highest_avg_region = avg_by_region.idxmax()

print("ANALYSIS COMPLETE ✅")
print(f"Top region         : {top_region} (GH₵ {top_rev:,.0f} — {top_share:.1f}% of total)")
print(f"Top category       : {top_cat}")
print(f"Best quarter       : {top_q} (GH₵ {top_q_rev:,.0f})")
print(f"Top channel        : {top_channel}")
print(f"Top sales rep      : {top_rep} (GH₵ {top_rep_rev:,.0f})")
print(f"Highest avg/sale   : {highest_avg_region} (GH₵ {avg_by_region.max():,.0f} per transaction)")
"""))

cells.append(new_markdown_cell("""\
### Stage 5 — Insights & Export
"""))

cells.append(new_code_cell("""\
# ── Print the business report ────────────────────────────────
print("=" * 70)
print("  GHANA REGIONAL SALES ANALYSIS — ANNUAL REPORT 2023")
print("=" * 70)

insights = [
    f"{top_region} generated the most revenue in 2023 — GH₵ {top_rev:,.0f}, "
    f"representing {top_share:.1f}% of all national sales. This reflects "
    f"Greater Accra's dominance as Ghana's commercial hub.",

    f"{top_cat} was the highest-grossing product category, driven by "
    f"high unit prices and consistent demand across all regions.",

    f"Sales peaked in {top_q} (GH₵ {top_q_rev:,.0f}), suggesting seasonal "
    f"demand patterns worth investigating for inventory planning.",

    f"The {top_channel} channel leads in revenue, though Wholesale "
    f"transactions tend to have higher average order values — "
    f"indicating a different customer profile worth targeting separately.",

    f"{top_rep} was the top-performing sales representative with "
    f"GH₵ {top_rep_rev:,.0f} in total sales. Understanding their "
    f"approach could help improve performance across the team.",

    f"Q1 → Q4 growth varied significantly by region — some regions "
    f"showed strong year-end surges while others declined. "
    f"Regional strategy should reflect these differences.",
]

for i, insight in enumerate(insights, 1):
    print(f"\\n  {i}. {insight}")
print("\\n" + "=" * 70)
"""))

cells.append(new_code_cell("""\
# ── Build the summary export ──────────────────────────────────
summary = df.groupby(["region","product_category","quarter"]).agg(
    transactions     = ("sale_id",           "count"),
    total_units      = ("units_sold",         "sum"),
    total_revenue    = ("total_revenue_ghs",  "sum"),
    avg_revenue      = ("total_revenue_ghs",  "mean"),
).round(2).reset_index()

summary.to_csv("regional_sales_summary.csv", index=False)
print(f"✅ Summary exported: regional_sales_summary.csv")
print(f"   Rows: {len(summary)}")
print()
print("Preview:")
print(summary.head(10).to_string(index=False))
"""))

# ─────────────────────────────────────────────
# LIVE CODING — ECOMMERCE
# ─────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## ⚡ Live Coding — Ghana E-Commerce Orders

> **Instructions:** Upload `ecommerce_orders_800.csv` to Colab.  
> The instructor works through the regional sales data.  
> You apply the **same groupby tools** to Ghana e-commerce orders —  
> a domain you interact with every day.
"""))

cells.append(new_code_cell("""\
# ⚡ LIVE CODING 1 — Load and explore
ecom = pd.read_csv("ecommerce_orders_800.csv", parse_dates=["date"])

# YOUR CODE: shape, head, dtypes, missing values
"""))

cells.append(new_code_cell("""\
# ⚡ LIVE CODING 2 — Sort
# Top 10 orders by value
# YOUR CODE HERE
"""))

cells.append(new_code_cell("""\
# ⚡ LIVE CODING 3 — groupby basics
# Total orders and revenue per region
# YOUR CODE HERE
"""))

cells.append(new_code_cell("""\
# ⚡ LIVE CODING 4 — .agg() with multiple functions
# For each product_category: count, avg order value, total revenue
# YOUR CODE HERE
"""))

cells.append(new_code_cell("""\
# ⚡ LIVE CODING 5 — Filter then group
# Delivered orders only → average rating per category
delivered = ecom[ecom["order_status"] == "Delivered"].copy()
delivered["rating"] = pd.to_numeric(delivered["rating"], errors="coerce")

# YOUR CODE HERE
"""))

cells.append(new_code_cell("""\
# ⚡ LIVE CODING 6 — Crosstab
# payment_method × order_status — how many of each combination?
# YOUR CODE HERE
"""))

cells.append(new_code_cell("""\
# ⚡ LIVE CODING 7 — Mini insights
# Answer these three questions:

# Q1: Which region has the highest cancellation rate?
# (cancellations / total orders per region)

# Q2: Does MoMo payment correlate with faster delivery?
# (avg delivery_days by payment_method, delivered orders only)

# Q3: Which product category gets the best average rating?

# YOUR CODE HERE
"""))

cells.append(new_code_cell("""\
# ⚡ LIVE CODING 8 — Export your summary
# Group by customer_region and product_category
# Export to ecommerce_summary.csv
# YOUR CODE HERE
"""))

# ─────────────────────────────────────────────
# CLOSING
# ─────────────────────────────────────────────
cells.append(new_markdown_cell("""\
---
## ✅ What You Covered in This Notebook

| Concept | pandas Tool |
|---------|------------|
| Rank data | `.sort_values(ascending=False)` |
| Group by one column | `df.groupby("col")["val"].sum()` |
| Group by multiple columns | `df.groupby(["col1","col2"])` |
| Multiple stats per group | `.agg(name=("col","func"))` |
| Filter then group | `df[condition].groupby(...)` |
| Cross-tabulation | `pd.crosstab(rows, cols, values, aggfunc)` |
| Quarter-on-quarter growth | `(q4 - q1) / q1 * 100` |
| Export results | `.to_csv(index=False)` |
| Add totals to crosstab | `.sum(axis=1)` and `.loc["TOTAL"]` |

---

## 🏆 Week 3 Complete!

You have now covered the full analyst toolkit for working with real data:

| Topic | Skill |
|-------|-------|
| 13 — Data Types & Dictionaries | Understand and model structured data |
| 14 — File Handling | Load and process raw files |
| 15 — NumPy | Fast numerical computation on arrays |
| 16 — Pandas Intro | Load, explore, filter, and select data |
| 17 — Data Cleaning | Fix real-world data quality problems |
| 18 — Analysis & Grouping | Answer business questions from data |

---

**Next → Week 3 End-of-Week Project 🏁**  
You will receive the `regional_sales_1000.csv` dataset and  
work through the full pipeline independently —  
from raw data to a formatted report with insights.
"""))

# ─────────────────────────────────────────────
# ASSEMBLE AND SAVE
# ─────────────────────────────────────────────
nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}
nb.metadata["language_info"] = {"name": "python", "version": "3.10.0"}

OUTPUT = "./topic18_analysis_grouping.ipynb"
with open(OUTPUT, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print(f"✅ Notebook written: {OUTPUT}")
print(f"   Total cells: {len(cells)}")
