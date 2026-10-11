"""Generates every Topic 21 (Data Visualization) notebook:
  topic21_data_visualization.ipynb
  topic21a_anatomy_of_a_chart.ipynb .. topic21g_visualization_practice.ipynb
  assignments/topic21_assignment_trading_dashboard.ipynb
  ../instructor_solutions/data_visualization/topic21_assignment_trading_dashboard_solutions.ipynb

Run: python build_topic21_notebooks.py
"""
from pathlib import Path

import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

HERE = Path(__file__).parent


def md(text):
    return new_markdown_cell(text.strip("\n"))


def code(text):
    return new_code_cell(text.strip("\n"))


def nb(cells):
    return new_notebook(cells=cells, metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    })


def write(notebook, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, path)
    print(f"wrote {path} ({len(notebook.cells)} cells)")


# ---------------------------------------------------------------------------
# Shared snippets reused across every Topic 21 notebook
# ---------------------------------------------------------------------------

def setup_cell(extra_candidate):
    """The find_data_dir() + palette + analysis-table setup cell.

    extra_candidate: the lesson-folder-relative candidate path, e.g.
    'data_visualization'. Mirrors Topic 20's find_data_dir() exactly, plus
    the chart palette and the rebuilt analysis table.
    """
    return code(f'''
# Run this cell as it is.
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


def find_data_dir():
    """Locate the lesson's data folder from the repository root, the lesson
    folder, or the assignments folder, so this notebook runs from anywhere."""
    candidates = [
        Path.cwd() / "data",
        Path.cwd() / "{extra_candidate}" / "data",
        Path.cwd().parent / "data",
    ]
    for candidate in candidates:
        if (candidate / "orders.csv").exists():
            return candidate
    raise FileNotFoundError(
        "Could not find orders.csv. Expected a data folder containing the six "
        "Topic 20/21 tables. Looked in: " + ", ".join(str(c) for c in candidates)
    )


DATA_DIR = find_data_dir()

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 130)
plt.rcParams["figure.figsize"] = (10, 5)
plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.color"] = "#e1e0d9"
plt.rcParams["grid.linewidth"] = 0.8
plt.rcParams["axes.edgecolor"] = "#c3c2b7"
plt.rcParams["axes.axisbelow"] = True

# The course palette. Hues are assigned in this fixed order to every chart in
# Topic 21 - never cycled, never re-generated - so a category keeps the same
# colour in every chart it appears in. See 21a for why this matters.
PALETTE = {{
    "blue": "#2a78d6", "aqua": "#1baf7a", "yellow": "#eda100", "green": "#008300",
    "violet": "#4a3aa7", "red": "#e34948", "magenta": "#e87ba4", "orange": "#eb6834",
}}
MUTED = "#c3c2b7"    # de-emphasis grey, for "everything but the finding"
INK = "#0b0b0b"      # text and value labels

# Fixed colour assignment per category, used throughout this topic.
ZONE_COLOR = {{"Coastal": PALETTE["blue"], "Middle": PALETTE["aqua"], "Northern": PALETTE["yellow"]}}
CHANNEL_COLOR = {{"Field Agent": PALETTE["blue"], "Online": PALETTE["aqua"],
                 "Phone": PALETTE["yellow"], "Shop": PALETTE["green"]}}
SEGMENT_COLOR = {{"Retail": PALETTE["blue"], "Wholesale": PALETTE["aqua"], "Institution": PALETTE["yellow"]}}
CATEGORY_COLOR = {{
    "Beverages": PALETTE["blue"], "Grains": PALETTE["aqua"], "Cooking Oils": PALETTE["yellow"],
    "Personal Care": PALETTE["green"], "Household": PALETTE["violet"], "Snacks": PALETTE["red"],
    "Canned Goods": PALETTE["magenta"],
}}

print("pandas version:   ", pd.__version__)
print("data folder:      ", DATA_DIR)
print("files:            ", sorted(p.name for p in DATA_DIR.glob("*.csv")))
'''.rstrip())


def rebuild_analysis_cell():
    return code('''
# Paste the function you built in Topic 20. This is the same contract: five
# raw tables in, one analysis-ready table out, with its own row-count check.
def clean_region(series):
    return (series.str.strip()
                  .str.replace(r"\\s+", " ", regex=True)
                  .str.title())


def build_analysis_table(orders, customers, products, regions, returns):
    """Combine the five raw tables into one analysis-ready table (Topic 20)."""
    expected_rows = len(orders)

    customers = customers.copy()
    customers["region"] = clean_region(customers["region"])
    products = products.drop_duplicates(subset="product_id", keep="first")
    customers = customers.merge(regions, on="region", how="left", validate="m:1")

    table = (orders
             .merge(customers, on="customer_id", how="left", validate="m:1")
             .merge(products, on="product_id", how="left", validate="m:1"))

    returned_ids = set(returns["order_id"])
    table["was_returned"] = table["order_id"].isin(returned_ids)

    table["order_date"] = pd.to_datetime(table["order_date"])
    table["month"] = table["order_date"].dt.strftime("%b")
    table["weekday"] = table["order_date"].dt.day_name()
    table["revenue_ghs"] = (table["quantity"] * table["unit_price_ghs"]).round(2)
    table["cost_ghs"] = (table["quantity"] * table["unit_cost_ghs"]).round(2)
    table["profit_ghs"] = (table["revenue_ghs"] - table["cost_ghs"]).round(2)

    if len(table) != expected_rows:
        raise ValueError(
            f"Row count changed during wrangling: {expected_rows} -> {len(table)}. "
            "A merge has duplicated rows."
        )
    return table.sort_values("order_date").reset_index(drop=True)


orders = pd.read_csv(DATA_DIR / "orders.csv")
customers = pd.read_csv(DATA_DIR / "customers.csv")
products = pd.read_csv(DATA_DIR / "products.csv")
regions = pd.read_csv(DATA_DIR / "regions.csv")
returns = pd.read_csv(DATA_DIR / "returns.csv")
targets_wide = pd.read_csv(DATA_DIR / "monthly_targets_wide.csv")

analysis = build_analysis_table(orders, customers, products, regions, returns)
print(f"Analysis table: {analysis.shape[0]} rows x {analysis.shape[1]} columns")
print(f"Total revenue: GHS {analysis['revenue_ghs'].sum():,.2f}")
print(f"Total profit:  GHS {analysis['profit_ghs'].sum():,.2f}")
'''.rstrip())


def footer_cell(back_main, prev, nxt):
    prev_line = f"- Previous: {prev}" if prev else "- Previous: [Main lesson](topic21_data_visualization.ipynb)"
    return md(f'''
---
## Where this fits

- [Back to the main lesson]({back_main})
{prev_line}
- Next: {nxt}
'''.rstrip())


def opening_cell(letter, title, scope, section_ref):
    return md(f'''
# Topic 21{letter} - {title}

{scope}

Work through it after reading section {section_ref} of the [main lesson](topic21_data_visualization.ipynb).
'''.rstrip())


def try_it_cell(number, prompt):
    return [md(f"### Try It {number} - {prompt}"), code("# YOUR CODE HERE")]


# ---------------------------------------------------------------------------
# Main lesson: topic21_data_visualization.ipynb
# ---------------------------------------------------------------------------

def build_main():
    cells = []

    cells.append(md('''
# Topic 21 - Data Visualization

## From one table to a picture someone can act on

In Topic 20 you built one analysis-ready table from five raw files, and used it to answer five of the director's questions - in code. That code was correct, but it was not something you could hand to her. A managing director does not read a DataFrame; she needs to see the answer in about five seconds, in a meeting, without you in the room to explain it.

**Data visualization** is the stage that turns a correct table into a chart that makes a finding impossible to miss. It is not decoration on top of the analysis - a badly chosen chart actively hides the finding underneath a technically correct one, and a well-chosen chart can make a finding obvious that was invisible in the table.

This lesson works with the *same* Ghanaian retail distributor from Topic 20 - the same six tables, the same four seeded data-quality problems, the same 2023 trading year. Nothing new to wrangle. Every chart in this lesson answers a question that table could already answer in numbers; the only new skill is choosing the right picture and building it so it reads correctly on its own.
'''))

    cells.append(md('''
## Learning objectives

By the end of this lesson you should be able to:

- explain the Figure/Axes model that every matplotlib chart is built from;
- choose a chart type from the question being asked, not from habit;
- build bar charts that compare categories correctly: sorted, labelled, one colour per series;
- build line charts that show change over time, with a rolling average to separate signal from noise;
- build histograms and box plots that reveal a distribution's shape, spread, and outliers;
- build scatter plots and a correlation heatmap that test whether two things are actually related;
- use a pie or waffle chart only when it is the right tool, and explain why that is rare;
- use seaborn to get the same charts faster, with better defaults;
- assemble several charts into a single dashboard figure that a non-technical reader can act on in one glance;
- state, for any chart you build, who reads it and what they should do next.
'''))

    cells.append(md('''
## Analysis compared with visualization

| | Analysis (Topic 20) | Visualization (Topic 21) |
|---|---|---|
| Output | A table of numbers | A picture |
| Audience | You, and other analysts | A manager, in a meeting, without you there to narrate |
| Primary tool | `pandas` | `matplotlib`, `seaborn` |
| A result is right when | The numbers are verified | The numbers are verified **and** the chart reads correctly alone, in five seconds |
| Typical failure | A silent bad join | A chart that is technically correct but misleads anyway |

That last row is the one students underestimate. A dual-axis chart, a rainbow of colours with no meaning, a pie chart with eleven slices - none of these are *wrong* in the sense of containing bad numbers. They are wrong because a reader draws the wrong conclusion from them anyway. Chart-building has its own silent failures, exactly the way joins did in Topic 20, and this lesson spends as much time on what **not** to build as on what to build.
'''))

    cells.append(setup_cell("data_visualization"))
    cells.append(rebuild_analysis_cell())

    cells.append(md("---"))
    cells.append(md('''
## The anatomy of a chart

Every matplotlib chart is two objects: a **Figure** (the whole canvas, which can hold several charts) and one or more **Axes** (a single plot, with its own x-axis, y-axis, title, and data). You will see `fig, ax = plt.subplots()` at the top of almost every cell in this lesson - that line creates both objects in one call and hands you `ax` to draw on.

A chart that is ready to hand to someone else has, at minimum: a title that states the finding, axis labels that include units, a legend if there is more than one series, and - for work you did not do yourself the day you present it - a note on where the data came from. Everything else is detail.
'''))
    cells.append(code('''
fig, ax = plt.subplots(figsize=(8, 4.5))

weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
orders_by_weekday = analysis["weekday"].value_counts().reindex(weekday_order)

ax.bar(orders_by_weekday.index, orders_by_weekday.values,
       color=PALETTE["blue"])

ax.set_title("Orders peak midweek and on Sundays")
ax.set_xlabel("Day of the week")
ax.set_ylabel("Number of orders in 2023")
ax.tick_params(axis="x", rotation=30)

fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
Five things happened in that cell that belong in every chart you build from here on:

1. `fig, ax = plt.subplots(...)` - create the canvas and the plot.
2. `ax.bar(...)` - draw the data. One call, one colour, because this is one series (order count) across categories that have no natural ranking - see the chart-selection rule below for why that matters.
3. `ax.set_title(...)` states the finding - "orders peak midweek and on Sundays" - not the generic label "Orders by weekday."
4. `ax.set_xlabel` / `ax.set_ylabel` name the axis **and its unit** ("Number of orders in 2023", not just "Orders").
5. `fig.tight_layout()` before `plt.show()`, so labels do not get clipped.

Section 21a goes through the Figure/Axes model in full, including multi-panel figures with `plt.subplots(rows, cols)` - the thing you will need for the dashboard at the end of this lesson.
'''))

    cells.append(md("---"))
    cells.append(md('''
## The chart-selection rule

Topic 19 and Topic 20 already gave you half of this rule: *line for change over time, bar for comparing categories.* That rule was correct as far as it went. Here is the rest of it.

| Question it answers | Chart | Why |
|---|---|---|
| How do these categories compare? | Bar (sorted, one colour) | Length is the easiest visual quantity for a reader to compare accurately |
| How did one thing change over time? | Line | Position along a continuous axis shows a trend; a bar chart over time hides it in a forest of rectangles |
| What does this distribution look like - where does it cluster, how far does it spread, are there outliers? | Histogram, box plot | Bar and line charts assume one number per category; a distribution is many numbers for *one* category |
| Are two numeric things related? | Scatter plot | The only chart that plots two measures against each other point by point |
| How do many pairs of things relate at once? | Heatmap | A grid of colour reads faster than a grid of numbers, for the same reason a bar reads faster than a table |
| How does a whole break into its parts? | Bar (stacked or sorted) first; pie or waffle only for a single, instantly-read snapshot of five categories or fewer | Comparing slice angles is a harder visual task than comparing bar lengths - see the composition section below |

Two rules sit underneath that table, and they are not optional:

- **One series, one colour.** If a bar chart has one bar per category and the categories have no natural order, every bar gets the *same* colour. Colouring each bar a different hue does not add information - the category names on the axis already identify them - it just spends the reader's attention on nothing. Reach for colour only when colour is doing a second job: telling two or more *series* apart, or marking the one bar that is the finding (see "emphasis" below).
- **Never two y-axes on one plot.** A chart with revenue on the left axis and order count on the right invents a correlation that is not in the data, because the two scales are lined up arbitrarily. If you need to compare two measures of different sizes, use two charts, or index both to a common start point.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Comparing categories: the bar family

Here is the bar chart from the end of Topic 20 - profit by zone, which answered "which zone produced the most profit?"
'''))
    cells.append(code('''
# The Topic 20 version: correct numbers, default styling.
zone_profit = analysis.groupby("zone")["profit_ghs"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(zone_profit.index, zone_profit.values)
ax.set_title("Profit by zone")
plt.show()
'''))
    cells.append(md('''
That chart is not wrong. It is also not finished: no units on the axis, a title that describes the chart instead of stating the finding, and no indication of which bar actually matters. Here is the same data, built to the standard the rest of this course now expects - using **emphasis**: colour the one bar that is the finding, and grey out the rest.
'''))
    cells.append(code('''
fig, ax = plt.subplots(figsize=(8, 4.5))

colors = [PALETTE["blue"] if zone == zone_profit.index[0] else MUTED
          for zone in zone_profit.index]
bars = ax.bar(zone_profit.index, zone_profit.values, color=colors)
ax.bar_label(bars, fmt="GHS %.0f", fontsize=9, padding=3)

ax.set_title(f"{zone_profit.index[0]} produced the most profit of any zone in 2023")
ax.set_xlabel("Zone")
ax.set_ylabel("Profit (GHS)")
ax.set_ylim(0, zone_profit.values.max() * 1.15)

fig.tight_layout()
plt.show()

margin = (analysis.groupby("zone").apply(
    lambda g: g["profit_ghs"].sum() / g["revenue_ghs"].sum() * 100, include_groups=False)
    .sort_values(ascending=False))
print("But profit MARGIN tells a different story - highest to lowest:")
print(margin.round(1).to_string())
'''))
    cells.append(md('''
Read that last line before moving on. Middle produced the most profit in cash terms (GHS 24,269.81), but Northern converted a larger *share* of its revenue into profit (29.7% margin, against Middle's 28.2%). Two bar charts of the same three zones, one answering "who made the most money" and the other "who ran the tightest operation," give two different answers - and a dashboard that shows only one of them is not lying, but it is not telling the whole story either. Section 21b covers grouped bars, stacked bars, and horizontal bars for long category names.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Change over time: the line family

A single line, one colour, is the right chart for "did revenue change over the year?" But a raw monthly line is noisy enough to hide the answer. Adding a rolling average - the technique from Topic 20's window-functions section - separates the trend from the month-to-month wobble.
'''))
    cells.append(code('''
monthly_revenue = (analysis.groupby(analysis["order_date"].dt.to_period("M"))["revenue_ghs"]
                           .sum())
monthly_revenue.index = monthly_revenue.index.astype(str)
rolling_3m = monthly_revenue.rolling(3).mean()

fig, ax = plt.subplots(figsize=(10, 4.5))

ax.plot(monthly_revenue.index, monthly_revenue.values,
        color=MUTED, linewidth=1.5, marker="o", markersize=4, label="Monthly revenue")
ax.plot(monthly_revenue.index, rolling_3m.values,
        color=PALETTE["blue"], linewidth=2.5, label="3-month rolling average")

ax.set_title("Revenue climbed sharply in the last two months of 2023")
ax.set_xlabel("Month of 2023")
ax.set_ylabel("Revenue (GHS)")
ax.tick_params(axis="x", rotation=45)
ax.legend(frameon=False)

fig.tight_layout()
plt.show()

jan_oct = monthly_revenue.iloc[0:10].mean()
nov_dec = monthly_revenue.iloc[10:12].mean()
print(f"Jan-Oct average:  GHS {jan_oct:,.2f} per month")
print(f"Nov-Dec average:  GHS {nov_dec:,.2f} per month ({(nov_dec / jan_oct - 1) * 100:.1f}% higher)")
'''))
    cells.append(md('''
Notice the colour choice: the raw monthly line is **muted grey** and the rolling average is the one in the course blue, with both labelled in a legend. That is the "emphasis" pattern again, applied to a line chart instead of a bar chart - context in grey, finding in colour. Section 21c covers multi-series lines (one line per zone) and when a rolling window is the wrong tool.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Distributions: histogram and box plot

Every chart so far has plotted one number per category or one number per month. A **distribution** is many numbers for the same thing - every individual order's revenue, for instance - and a bar or line chart cannot show it. A histogram bins the values and counts how many fall in each bin; a box plot summarises the same information as five numbers (minimum, 25th percentile, median, 75th percentile, maximum) that you can compare across groups.
'''))
    cells.append(code('''
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

axes[0].hist(analysis["revenue_ghs"], bins=40, color=PALETTE["blue"], edgecolor="white")
axes[0].axvline(analysis["revenue_ghs"].mean(), color=PALETTE["red"], linewidth=2,
                 label=f"Mean: GHS {analysis['revenue_ghs'].mean():,.0f}")
axes[0].axvline(analysis["revenue_ghs"].median(), color=INK, linewidth=2, linestyle=(0, (4, 2)),
                 label=f"Median: GHS {analysis['revenue_ghs'].median():,.0f}")
axes[0].set_title("Order revenue is heavily right-skewed")
axes[0].set_xlabel("Order revenue (GHS)")
axes[0].set_ylabel("Number of orders")
axes[0].legend(frameon=False)

segment_order = ["Institution", "Wholesale", "Retail"]
box_data = [analysis.loc[analysis["segment"] == seg, "profit_ghs"].dropna() for seg in segment_order]
bp = axes[1].boxplot(box_data, tick_labels=segment_order, patch_artist=True, showfliers=True,
                      flierprops={"markersize": 3, "markerfacecolor": MUTED, "markeredgecolor": "none"})
for patch, seg in zip(bp["boxes"], segment_order):
    patch.set_facecolor(SEGMENT_COLOR[seg])
    patch.set_alpha(0.85)
axes[1].set_title("Wholesale orders are the most profitable, but also the most variable")
axes[1].set_xlabel("Segment")
axes[1].set_ylabel("Profit per order (GHS)")

fig.tight_layout()
plt.show()

q1, q3 = analysis["revenue_ghs"].quantile([0.25, 0.75])
fence = q3 + 1.5 * (q3 - q1)
print(f"Mean order revenue (GHS {analysis['revenue_ghs'].mean():,.2f}) is more than double the median "
      f"(GHS {analysis['revenue_ghs'].median():,.2f}) - a few large orders pull it up.")
print(f"Orders above GHS {fence:,.2f} (the IQR outlier fence): "
      f"{(analysis['revenue_ghs'] > fence).sum()} of {len(analysis)} "
      f"({(analysis['revenue_ghs'] > fence).mean() * 100:.1f}%).")
'''))
    cells.append(md('''
That mean-versus-median gap is the whole reason distributions get their own chart type. If you only ever reported "average order revenue is GHS 191.67," you would be describing a typical order that barely exists - half of all orders are under GHS 72.16. A histogram shows you that shape in one look; a single summary number hides it. Section 21d covers reading a box plot's five numbers precisely and when a log scale helps a skewed histogram.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Relationships: scatter plot and correlation heatmap

A scatter plot tests whether two numeric measures move together. It is also the chart most likely to show you that two things you expected to be related... are not.
'''))
    cells.append(code('''
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].scatter(analysis["unit_price_ghs"], analysis["quantity"],
                s=18, alpha=0.4, color=PALETTE["blue"], edgecolors="none")
r_qp = analysis["quantity"].corr(analysis["unit_price_ghs"])
axes[0].set_title(f"Order size does not depend on unit price (r = {r_qp:.2f})")
axes[0].set_xlabel("Unit price (GHS)")
axes[0].set_ylabel("Quantity ordered")

numeric_cols = ["quantity", "unit_price_ghs", "revenue_ghs", "cost_ghs", "profit_ghs"]
corr = analysis[numeric_cols].corr()
im = axes[1].imshow(corr, cmap="RdBu", vmin=-1, vmax=1)
axes[1].set_xticks(range(len(numeric_cols)))
axes[1].set_yticks(range(len(numeric_cols)))
axes[1].set_xticklabels(numeric_cols, rotation=45, ha="right")
axes[1].set_yticklabels(numeric_cols)
for i in range(len(numeric_cols)):
    for j in range(len(numeric_cols)):
        axes[1].text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center",
                      color="white" if abs(corr.iloc[i, j]) > 0.6 else INK, fontsize=9)
axes[1].set_title("Revenue and profit move almost together (r = 0.98)")
fig.colorbar(im, ax=axes[1], shrink=0.85, label="Correlation")

fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
Two choices in that heatmap are deliberate, not default. First, the colour scale runs from **-1 to +1** even though every value here happens to be positive - correlation is a signed measure, and fixing the scale lets a reader compare this heatmap to any other one honestly. Second, the colour map is **diverging** (blue to white to red) rather than a single hue, because zero correlation is a meaningful midpoint ("no relationship"), not just a low value. Section 21e covers bubble charts (a third, size-encoded variable) and reshaping a table into the wide grid a heatmap needs.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Composition charts, used sparingly

A pie or waffle chart answers "how does a whole break into its parts," in a single glance, for a small number of parts. That is a real, narrow job - and most of the time a sorted bar chart does that job better, because comparing bar *lengths* is a task the human eye is good at, while comparing slice *angles* is a task it is measurably worse at. The channel mix below is a legitimate case: four categories, genuinely summing to 100% of 2023 revenue, read once as a snapshot.
'''))
    cells.append(code('''
channel_share = (analysis.groupby("channel")["revenue_ghs"].sum()
                  .pipe(lambda s: s / s.sum() * 100).round(1)
                  .sort_values(ascending=False))
colors = [CHANNEL_COLOR[ch] for ch in channel_share.index]

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

axes[0].pie(channel_share.values, labels=channel_share.index, colors=colors,
            autopct="%1.0f%%", startangle=90, pctdistance=0.75,
            wedgeprops={"edgecolor": "white", "linewidth": 1.5})
axes[0].set_title("2023 revenue share by channel")

bars = axes[1].barh(channel_share.index[::-1], channel_share.values[::-1],
                     color=[CHANNEL_COLOR[ch] for ch in channel_share.index[::-1]])
axes[1].bar_label(bars, fmt="%.0f%%", padding=3)
axes[1].set_title("The same numbers, as a sorted bar")
axes[1].set_xlabel("Share of 2023 revenue (%)")
axes[1].set_xlim(0, channel_share.max() * 1.2)

fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
Look at the two charts side by side and ask yourself honestly which one let you rank the four channels faster. For most readers it is the bar on the right, even though the pie is not wrong. This is why the chart-selection rule above puts composition last, and gates it at "five categories or fewer" - a seven-slice pie (try it on the product categories) stops being readable as *anything*.

A **waffle chart** - a grid of squares, one square per percentage point - is the other composition option, and it has one advantage a pie does not: it survives being printed in black and white, using hatch patterns instead of colour.
'''))
    cells.append(code('''
segment_share = (customers["segment"].value_counts(normalize=True) * 100).round(0).astype(int)
segment_share = segment_share.sort_values(ascending=False)

hatches = ["///", "...", "xxx"]
fig, ax = plt.subplots(figsize=(6, 6))
rows, cols = 10, 10
square = 0
for (label, pct), hatch in zip(segment_share.items(), hatches):
    for _ in range(pct):
        r, c = divmod(square, cols)
        ax.add_patch(plt.Rectangle((c, rows - 1 - r), 1, 1, facecolor="white",
                                    edgecolor="black", hatch=hatch, linewidth=0.6))
        square += 1

handles = [plt.Rectangle((0, 0), 1, 1, facecolor="white", edgecolor="black", hatch=h)
           for h in hatches]
ax.legend(handles, [f"{label} ({pct}%)" for label, pct in segment_share.items()],
          loc="upper center", bbox_to_anchor=(0.5, -0.05), ncol=3, frameon=False)
ax.set_xlim(0, cols)
ax.set_ylim(0, rows)
ax.set_aspect("equal")
ax.set_xticks([])
ax.set_yticks([])
ax.set_title("Customers by segment, one square per percentage point")
fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
Reach for hatch patterns instead of colour whenever the chart has to survive without colour - a black-and-white printout, a photocopy, or a reader with colour-vision deficiency who cannot tell your blue bar from your red one. It is not a style choice to use by default; it is an accessibility fallback to have ready. Section 21f covers both chart types in full, including when a waffle chart is a worse choice than the bar you already know how to build.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Seaborn: the same charts, faster

`seaborn` is a layer on top of matplotlib that knows about DataFrames and groups, so charts that took several lines above take one. It does not replace anything you just learned - a seaborn chart is still a matplotlib Figure and Axes underneath, and everything about titles, labels, and colour choice above still applies.
'''))
    cells.append(code('''
import seaborn as sns

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

category_revenue = analysis.groupby("category")["revenue_ghs"].sum().sort_values(ascending=False)
sns.barplot(x=category_revenue.values, y=category_revenue.index, ax=axes[0],
            color=PALETTE["blue"])
axes[0].set_title("Grains alone drove 42% of 2023 revenue")
axes[0].set_xlabel("Revenue (GHS)")
axes[0].set_ylabel("Category")

sns.regplot(data=analysis, x="quantity", y="revenue_ghs", ax=axes[1],
            scatter_kws={"s": 16, "alpha": 0.35, "color": PALETTE["blue"]},
            line_kws={"color": PALETTE["red"]})
axes[1].set_title(f"Revenue rises with order size (r = {analysis['quantity'].corr(analysis['revenue_ghs']):.2f})")
axes[1].set_xlabel("Quantity ordered")
axes[1].set_ylabel("Order revenue (GHS)")

fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
`sns.barplot` took one line to do what the earlier bar charts needed several for, and `sns.regplot` added a fitted trend line to a scatter plot for free. The trade-off: seaborn makes its own styling decisions unless you override them, which is why every chart above still sets its own colour explicitly from `PALETTE` rather than letting seaborn pick. Section 21f covers `sns.set_theme()`, seaborn's categorical and statistical plot types, and building a multi-panel figure with seaborn charts inside matplotlib's `subplots()` grid.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Put it together: the director's dashboard

Four charts, four different chart types, one figure - because the director's questions span comparison, time, and performance against target, and no single chart type answers all three.
'''))
    cells.append(code('''
# Panel data, reusing Topic 20's reshaping and this lesson's chart selection.
targets_long = targets_wide.melt(id_vars="region", var_name="month", value_name="target_ghs")
actual_by_region_month = analysis.groupby(["region", "month"])["revenue_ghs"].sum().reset_index()
perf = targets_long.merge(actual_by_region_month, on=["region", "month"], how="left", validate="1:1")
perf["revenue_ghs"] = perf["revenue_ghs"].fillna(0.0)

region_annual = (perf.groupby("region")[["target_ghs", "revenue_ghs"]].sum())
region_annual["shortfall_ghs"] = (region_annual["target_ghs"] - region_annual["revenue_ghs"]).round(2)
region_annual = region_annual.sort_values("shortfall_ghs", ascending=True)  # most-ahead first

category_revenue = analysis.groupby("category")["revenue_ghs"].sum().sort_values(ascending=True)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Profit by zone, emphasis on the leader.
zone_profit = analysis.groupby("zone")["profit_ghs"].sum().sort_values(ascending=False)
colors = [PALETTE["blue"] if z == zone_profit.index[0] else MUTED for z in zone_profit.index]
bars = axes[0, 0].bar(zone_profit.index, zone_profit.values, color=colors)
axes[0, 0].bar_label(bars, fmt="GHS %.0f", fontsize=9, padding=3)
axes[0, 0].set_title("Middle produced the most profit of any zone")
axes[0, 0].set_ylabel("Profit (GHS)")

# 2. Monthly revenue with rolling average.
monthly_revenue = analysis.groupby(analysis["order_date"].dt.to_period("M"))["revenue_ghs"].sum()
monthly_revenue.index = monthly_revenue.index.astype(str)
axes[0, 1].plot(monthly_revenue.index, monthly_revenue.values, color=MUTED,
                 marker="o", markersize=4, linewidth=1.5, label="Monthly")
axes[0, 1].plot(monthly_revenue.index, monthly_revenue.rolling(3).mean().values,
                 color=PALETTE["blue"], linewidth=2.5, label="3-month average")
axes[0, 1].set_title("Revenue rose sharply in Nov-Dec 2023")
axes[0, 1].set_ylabel("Revenue (GHS)")
axes[0, 1].tick_params(axis="x", rotation=45)
axes[0, 1].legend(frameon=False, fontsize=8)

# 3. Region performance against target - diverging.
colors = [PALETTE["red"] if v > 0 else PALETTE["blue"] for v in region_annual["shortfall_ghs"]]
axes[1, 0].barh(region_annual.index, -region_annual["shortfall_ghs"], color=colors)
axes[1, 0].axvline(0, color=INK, linewidth=1)
axes[1, 0].set_title("3 of 16 regions beat target; Bono missed by the widest margin")
axes[1, 0].set_xlabel("GHS ahead of target (+) / behind target (-)")
axes[1, 0].tick_params(axis="y", labelsize=7)

# 4. Category revenue, sorted, emphasis on the leader.
colors = [PALETTE["blue"] if c == category_revenue.index[-1] else MUTED for c in category_revenue.index]
bars = axes[1, 1].barh(category_revenue.index, category_revenue.values, color=colors)
axes[1, 1].set_title("Grains is the largest revenue category by a wide margin")
axes[1, 1].set_xlabel("Revenue (GHS)")

fig.suptitle("2023 Trading Review - at a glance", fontsize=15, y=1.0)
fig.tight_layout()

charts_dir = Path("charts")
charts_dir.mkdir(exist_ok=True)
fig.savefig(charts_dir / "director_dashboard.png", dpi=150, bbox_inches="tight")
plt.show()

print(f"Saved to {charts_dir / 'director_dashboard.png'}")
'''))
    cells.append(md('''
Every panel in that figure is a chart type this lesson already justified: emphasis bar, line-with-rolling-average, diverging bar, sorted horizontal bar. Nothing in it is a pie, a dual axis, or a rainbow of unexplained colours. That restraint is the point - a dashboard is not "put every chart you know how to make on one page," it is "pick the four chart types that each answer one real question, and say no to the rest."
'''))

    cells.append(md("---"))
    cells.append(md('''
## Key takeaways

- **A chart has to read correctly alone**, in five seconds, without you in the room - that is a harder bar than "the numbers are correct."
- Every chart is a **Figure** and one or more **Axes**; `fig, ax = plt.subplots()` is the line you will write most often in this topic.
- The chart-selection rule: **bar** for comparing categories, **line** for change over time, **histogram/box** for a distribution's shape, **scatter** for a relationship between two numbers, **heatmap** for many relationships at once, **pie/waffle** only for a single snapshot of five categories or fewer.
- **One series, one colour**, when categories have no natural order. Colour is for telling series apart or marking the finding - not decoration.
- **Emphasis** - one bar or line in the course colour, everything else in grey - is usually a better choice than a different hue per category.
- **Never two y-axes on one plot.** It invents a correlation that is not in the data.
- A **correlation heatmap** is a diverging chart (fix the scale at -1 to +1), because zero is a meaningful midpoint, not just a low value.
- **Mean and median can tell different stories.** A histogram shows you the shape a single summary number hides.
- A pie or waffle chart is the exception, not the default - a sorted bar almost always makes the same comparison easier to read.
- `seaborn` builds the same matplotlib Figure/Axes faster, with statistical extras like a fitted regression line - it does not replace anything you learned about titles, labels, or colour.
- A **dashboard** is a small, deliberate set of chart types, each answering one real question - not every chart you can make, arranged on one page.
'''))

    cells.append(md('''
## Further reading and the course path

### matplotlib and seaborn documentation
- [matplotlib: Quick start guide](https://matplotlib.org/stable/users/explain/quick_start.html)
- [matplotlib: `pyplot.subplots`](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html)
- [matplotlib: Choosing colormaps](https://matplotlib.org/stable/users/explain/colors/colormaps.html)
- [seaborn: An introduction](https://seaborn.pydata.org/tutorial/introduction.html)
- [seaborn: Choosing color palettes](https://seaborn.pydata.org/tutorial/color_palettes.html)

### Background
- [Edward Tufte, "The Visual Display of Quantitative Information"](https://www.edwardtufte.com/tufte/books_vdqi) - the data-ink ratio and why chart-junk costs more than it looks like it does
- [Cole Nussbaumer Knaflic, "Storytelling with Data"](https://www.storytellingwithdata.com/) - on choosing a chart for the audience, not the data

### Practice notebooks for this topic
- [21a - Anatomy of a chart](topic21a_anatomy_of_a_chart.ipynb)
- [21b - Comparing categories](topic21b_comparing_categories.ipynb)
- [21c - Change over time](topic21c_change_over_time.ipynb)
- [21d - Distributions](topic21d_distributions.ipynb)
- [21e - Relationships](topic21e_relationships.ipynb)
- [21f - Composition and seaborn](topic21f_composition_and_seaborn.ipynb)
- [21g - Visualization practice](topic21g_visualization_practice.ipynb)

### Assignment
- [Topic 21 assignment - the director's dashboard](assignments/topic21_assignment_trading_dashboard.ipynb)

### Elsewhere in the course
- [Topic 19 - Data gathering](../data_analysis_process/topic19_data_gathering.ipynb)
- [Topic 20 - Data wrangling](../data_wrangling/topic20_data_wrangling.ipynb)
- [Submitting your work with GitHub](../data_analysis_process/topic19d_appendix_submitting_with_github.ipynb)
'''))

    return nb(cells)


# ---------------------------------------------------------------------------
# 21a - Anatomy of a chart
# ---------------------------------------------------------------------------

def build_21a():
    cells = [opening_cell(
        "a", "Anatomy of a chart",
        "Every matplotlib chart - every one you will build in this entire topic - is built from the same two kinds of object. This notebook makes that model explicit, then uses it to build multi-panel figures and save them to disk, both of which the rest of Topic 21 assumes you can already do.",
        "1",
    )]
    cells.append(setup_cell("data_visualization"))
    cells.append(rebuild_analysis_cell())

    cells.append(md("---"))
    cells.append(md('''
## Figure and Axes

A **Figure** is the whole canvas - the thing you save to a PNG. An **Axes** is one plot on that canvas, with its own x-axis, y-axis, title, and data. Most of the charts you have seen in other courses were built with `plt.bar(...)` or `plt.plot(...)` directly - that is a shortcut that quietly creates a Figure with one Axes for you. This course always creates both explicitly, because the shortcut stops working the moment you want more than one chart on a page.
'''))
    cells.append(code('''
fig, ax = plt.subplots(figsize=(7, 4))
print(type(fig))
print(type(ax))

orders_by_channel = analysis["channel"].value_counts()
ax.bar(orders_by_channel.index, orders_by_channel.values, color=PALETTE["blue"])
ax.set_title("Shop is the busiest channel by order count")
ax.set_xlabel("Channel")
ax.set_ylabel("Number of orders")
plt.show()
'''))
    cells.append(md('''
`figsize=(7, 4)` is in **inches**, not pixels - it matters when you save the figure, because the pixel count is `figsize * dpi`. The default `dpi` in this course is set once, in the setup cell (`plt.rcParams["figure.dpi"]`), so every chart in a notebook renders at a consistent size without repeating it.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Several Axes on one Figure

`plt.subplots(rows, cols)` returns one Figure and an **array** of Axes. The shape of that array depends on `rows` and `cols`, and this is the single most common beginner error in matplotlib: with one row, `axes` is a 1-D array and you index it `axes[1]`; with more than one row, it is 2-D and you index it `axes[1, 0]`. Mixing the two raises an `IndexError` that gives no hint about which assumption was wrong.
'''))
    cells.append(code('''
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
print("1 row:", type(axes), axes.shape)   # 1-D - axes[0], axes[1]

return_rate = (analysis.groupby("category")["was_returned"].mean() * 100).round(1).sort_values()
axes[0].barh(return_rate.index, return_rate.values, color=PALETTE["blue"])
axes[0].set_title("Return rate by category")
axes[0].set_xlabel("Return rate (%)")

order_count = analysis["category"].value_counts().reindex(return_rate.index)
axes[1].barh(order_count.index, order_count.values, color=PALETTE["aqua"])
axes[1].set_title("Order count by category")
axes[1].set_xlabel("Number of orders")

fig.tight_layout()
plt.show()
'''))
    cells.append(code('''
fig, axes = plt.subplots(2, 2, figsize=(10, 7))
print("2 rows:", type(axes), axes.shape)  # 2-D - axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

for ax in axes.flat:        # .flat gives you a 1-D view when you just need "every panel"
    ax.set_visible(False)   # placeholders - real panels go in the "put it together" sections

plt.show()
'''))
    cells.append(md('''
That second cell is why the main lesson's dashboard loops with `axes[0, 0]`, `axes[0, 1]`, `axes[1, 0]`, `axes[1, 1]` by name rather than a loop - with only four panels and four different chart types, explicit indexing is more readable than a loop would be. `axes.flat` is the tool for when you genuinely want to do the *same* thing to every panel.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Cleaning up the chrome

A default matplotlib Axes draws a box on all four sides and heavy-ish gridlines. Removing the top and right spines, and keeping gridlines thin and behind the data (`axes.axisbelow`, set once in this course's setup cell), reduces visual noise without losing any information - the data was never near the top or right edge anyway.
'''))
    cells.append(code('''
fig, ax = plt.subplots(figsize=(8, 4.5))

weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
orders_by_weekday = analysis["weekday"].value_counts().reindex(weekday_order)
ax.bar(orders_by_weekday.index, orders_by_weekday.values, color=PALETTE["blue"])

ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Orders peak midweek and on Sundays")
ax.set_xlabel("Day of the week")
ax.set_ylabel("Number of orders in 2023")

fig.tight_layout()
plt.show()
'''))

    cells.append(md('''
### Try It 1 - a labelled, two-panel figure

Build one Figure with two Axes side by side (`plt.subplots(1, 2, ...)`):

- left panel: a bar chart of total revenue by segment (`Retail`, `Wholesale`, `Institution`);
- right panel: a bar chart of number of orders by segment;
- both panels need a title that states what the chart shows, an x-axis label, and a y-axis label with units;
- remove the top and right spines on both panels.

Does the segment with the most orders also have the most revenue? Say so in a comment.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(md("---"))
    cells.append(md('''
## Saving a figure

`fig.savefig(...)` - never `plt.savefig(...)` once you are working with named Figures, for the same reason you address `ax` by name instead of relying on "whatever was drawn last." Call it **before** `plt.show()` - in some environments `plt.show()` clears the figure from memory, and a save after that point writes a blank image.
'''))
    cells.append(code('''
charts_dir = Path("charts")
charts_dir.mkdir(exist_ok=True)

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(orders_by_weekday.index, orders_by_weekday.values, color=PALETTE["blue"])
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Orders peak midweek and on Sundays")
ax.set_xlabel("Day of the week")
ax.set_ylabel("Number of orders in 2023")
fig.tight_layout()

fig.savefig(charts_dir / "orders_by_weekday.png", dpi=150, bbox_inches="tight")
plt.show()
print(f"Saved to {charts_dir / 'orders_by_weekday.png'}")
'''))
    cells.append(md('''
`dpi=150` is a reasonable default for a chart that will be viewed on screen or embedded in a README; use `dpi=300` for anything headed to print. `bbox_inches="tight"` trims the whitespace matplotlib otherwise leaves around the figure - without it, rotated tick labels are often clipped at the saved image's edge even though they looked fine in the notebook.
'''))

    cells.append(footer_cell(
        "topic21_data_visualization.ipynb", None,
        "[21b - Comparing categories](topic21b_comparing_categories.ipynb)",
    ))
    return nb(cells)


# ---------------------------------------------------------------------------
# 21b - Comparing categories (the bar family)
# ---------------------------------------------------------------------------

def build_21b():
    cells = [opening_cell(
        "b", "Comparing categories",
        "The bar chart is the workhorse of this course, and it comes in more shapes than the single sorted bar the main lesson showed. This notebook covers horizontal bars for long category names, grouped bars for two categorical dimensions at once, and stacked bars for part-to-whole - plus the one mistake (the 100%-stacked bar that hides the total) that undoes a stacked bar's main advantage.",
        "3",
    )]
    cells.append(setup_cell("data_visualization"))
    cells.append(rebuild_analysis_cell())

    cells.append(md("---"))
    cells.append(md('''
## Horizontal bars for long labels

A vertical bar chart rotates category labels when they are too long to fit, and rotated labels are harder to read than horizontal ones. `ax.barh()` swaps the problem away entirely - and it is also simply the better choice whenever the categories themselves are the point and the reader will scan down a ranked list, the way a report's table of contents reads top to bottom.
'''))
    cells.append(code('''
product_revenue = (analysis.groupby("product_name")["revenue_ghs"].sum()
                    .sort_values(ascending=True).tail(8))

fig, ax = plt.subplots(figsize=(8, 5))
colors = [PALETTE["blue"] if p == product_revenue.index[-1] else MUTED for p in product_revenue.index]
bars = ax.barh(product_revenue.index, product_revenue.values, color=colors)
ax.bar_label(bars, fmt="GHS %.0f", padding=3, fontsize=8)
ax.set_title("Perfumed Rice 25kg outsold every other product more than 2-to-1")
ax.set_xlabel("Revenue (GHS)")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
Note the sort: `ascending=True` with `.tail(8)` puts the **largest** value at the **top** of a horizontal bar chart, because matplotlib draws the first row at the bottom. This trips up almost everyone the first time - sorting ascending looks backwards until you remember which end of the y-axis is "first."
'''))

    cells.append(md("---"))
    cells.append(md('''
## Grouped bars: two categorical dimensions at once

A single bar chart compares one measure across one category. A **grouped bar chart** compares one measure across two categories at once - here, revenue by zone *and* channel - by clustering a small bar per channel within each zone's group. This is where categorical colour earns its place: each channel needs its own colour because a reader has to track it *across* zones, and that is identity, not magnitude.
'''))
    cells.append(code('''
pivot = analysis.pivot_table(index="zone", columns="channel", values="revenue_ghs", aggfunc="sum")
zone_order = ["Coastal", "Middle", "Northern"]
channel_order = ["Field Agent", "Online", "Phone", "Shop"]
pivot = pivot.loc[zone_order, channel_order]

x = np.arange(len(zone_order))
width = 0.2

fig, ax = plt.subplots(figsize=(10, 5))
for i, channel in enumerate(channel_order):
    ax.bar(x + (i - 1.5) * width, pivot[channel], width=width,
           label=channel, color=CHANNEL_COLOR[channel])

ax.set_xticks(x)
ax.set_xticklabels(zone_order)
ax.set_title("Shop leads revenue in every zone; Online is a strong second only in Middle")
ax.set_xlabel("Zone")
ax.set_ylabel("Revenue (GHS)")
ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12))
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
`x + (i - 1.5) * width` is the arithmetic that centres four bars per group around each tick: with four channels, offsets of `-1.5, -0.5, 0.5, 1.5` times the bar width spread them symmetrically. For a different number of series, the offset is `(i - (n - 1) / 2) * width`.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Stacked bars: part-to-whole across categories

A stacked bar shows the same grouped data as *one* bar per zone, with channels stacked inside it - trading the ability to compare channels precisely within a zone for the ability to compare zone **totals** at a glance, which a grouped bar cannot do.
'''))
    cells.append(code('''
fig, ax = plt.subplots(figsize=(9, 5))
bottom = np.zeros(len(zone_order))
for channel in channel_order:
    values = pivot[channel].values
    ax.bar(zone_order, values, bottom=bottom, label=channel, color=CHANNEL_COLOR[channel])
    bottom += values

ax.set_title("Middle has the highest total revenue of any zone")
ax.set_xlabel("Zone")
ax.set_ylabel("Revenue (GHS)")
ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.1))
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
Resist the urge to convert this to a **100%-stacked** bar (every bar scaled to the same height, showing channel *share* instead of channel *amount*) unless the total genuinely does not matter. A 100%-stacked bar answers "what share of Northern's revenue came from Shop" - a real question - but it throws away the fact that Northern's total revenue (GHS 60,805.78) is smaller than Middle's (GHS 86,094.31). If both the shares and the totals matter, that is two charts, not one.
'''))

    cells.append(md('''
### Try It 2 - grouped or stacked?

Build a chart of order **count** (not revenue) by segment and channel. Decide for yourself whether a grouped or a stacked bar answers "which channel does each segment prefer" more clearly, build that one, and leave a one-line comment explaining why you chose it over the other.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(footer_cell(
        "topic21_data_visualization.ipynb",
        "[21a - Anatomy of a chart](topic21a_anatomy_of_a_chart.ipynb)",
        "[21c - Change over time](topic21c_change_over_time.ipynb)",
    ))
    return nb(cells)


# ---------------------------------------------------------------------------
# 21c - Change over time (the line family)
# ---------------------------------------------------------------------------

def build_21c():
    cells = [opening_cell(
        "c", "Change over time",
        "The main lesson built one line with a rolling average. This notebook covers multiple lines on one Axes (one per zone), annotating the single point that matters instead of labelling every point, and a short case for when a rolling average is the wrong tool.",
        "4",
    )]
    cells.append(setup_cell("data_visualization"))
    cells.append(rebuild_analysis_cell())

    cells.append(md("---"))
    cells.append(md('''
## Multiple lines: one series per zone

The main lesson's "revenue rose in Nov-Dec" finding was true for the business as a whole. Splitting the same line by zone tests whether that is true everywhere, or driven by one zone alone.
'''))
    cells.append(code('''
analysis["period"] = analysis["order_date"].dt.to_period("M").astype(str)
by_zone = analysis.groupby(["period", "zone"])["revenue_ghs"].sum().unstack()
zone_order = ["Coastal", "Middle", "Northern"]
by_zone = by_zone[zone_order]

fig, ax = plt.subplots(figsize=(10, 5))
for zone in zone_order:
    ax.plot(by_zone.index, by_zone[zone], marker="o", markersize=4,
             linewidth=2, label=zone, color=ZONE_COLOR[zone])

ax.set_title("Middle's November spike, not a broad trend, drove the year-end jump")
ax.set_xlabel("Month of 2023")
ax.set_ylabel("Revenue (GHS)")
ax.tick_params(axis="x", rotation=45)
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
plt.show()

print("Peak month per zone:")
print(by_zone.idxmax().to_string())
'''))
    cells.append(md('''
That is the opposite of what the single-line chart in the main lesson implied. "Revenue rose in Nov-Dec" was true, but reading it as "the business had a strong finish" overstates it - Coastal and Northern had ordinary months in November, and Middle alone jumped from an October figure near GHS 6,500 to over GHS 17,400. A single aggregate line can genuinely hide which part of the business a finding belongs to. This is also why the course colour for each zone stays fixed across every chart in this topic (`ZONE_COLOR`, defined once in the setup cell) - a reader who learned "Middle is the aqua line" here should not have to relearn it in the next chart.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Direct labels instead of a cluttered legend

With three lines a legend box is fine. With more series than that, labelling the **end of each line** directly - instead of making a reader's eye jump between a line and a legend box - reads faster, and it is the "selective direct label" the chart-selection rule in the main lesson referred to.
'''))
    cells.append(code('''
fig, ax = plt.subplots(figsize=(10, 5))
for zone in zone_order:
    ax.plot(by_zone.index, by_zone[zone], linewidth=2, color=ZONE_COLOR[zone])
    ax.annotate(zone, xy=(len(by_zone) - 1, by_zone[zone].iloc[-1]),
                xytext=(6, 0), textcoords="offset points",
                va="center", color=ZONE_COLOR[zone], fontweight="bold")

ax.set_title("Middle's November spike, not a broad trend, drove the year-end jump")
ax.set_xlabel("Month of 2023")
ax.set_ylabel("Revenue (GHS)")
ax.tick_params(axis="x", rotation=45)
ax.set_xlim(right=len(by_zone) - 0.3)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
Note `ax.set_xlim(right=...)` - without extra room on the right, the direct labels collide with the plot's edge. This is a real trade-off: direct labels need that spare margin, and a legend does not. Neither is unconditionally better; pick based on how many series you have and how much horizontal room the figure can spare.
'''))

    cells.append(md("---"))
    cells.append(md('''
## When a rolling average is the wrong tool

A 3-month rolling average smooths monthly noise because there is enough history (12 months) for a 3-point window to still mean something. It stops being useful on a short series - averaging 3 of only 4 available data points barely smooths anything, and it drops the first two points from the chart entirely (there is no full window yet to average).
'''))
    cells.append(code('''
q1_2023 = analysis[analysis["order_date"] < "2023-04-01"]
weekly = q1_2023.groupby(q1_2023["order_date"].dt.to_period("W"))["revenue_ghs"].sum()
print(f"Only {len(weekly)} weekly data points in Q1 alone - a 3-month rolling average has nothing to work with here.")
print("For a short series, a shorter window (or no smoothing at all) is the honest choice.")
'''))

    cells.append(md('''
### Try It 3 - index two series to a common base

Plot monthly revenue for Coastal and Middle **indexed to January = 100** (divide every month by its January value and multiply by 100), on the same Axes, one line each. This is the "common base" fix the main lesson mentioned for comparing two series of different sizes on one axis, instead of a dual-axis chart. Which zone grew faster, relative to its own January?
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(footer_cell(
        "topic21_data_visualization.ipynb",
        "[21b - Comparing categories](topic21b_comparing_categories.ipynb)",
        "[21d - Distributions](topic21d_distributions.ipynb)",
    ))
    return nb(cells)


# ---------------------------------------------------------------------------
# 21d - Distributions
# ---------------------------------------------------------------------------

def build_21d():
    cells = [opening_cell(
        "d", "Distributions",
        "The main lesson showed one histogram and one box plot. This notebook covers reading a box plot's five numbers precisely, comparing more than two groups at once, and a log-scale histogram for the cases a linear one cannot show.",
        "5",
    )]
    cells.append(setup_cell("data_visualization"))
    cells.append(rebuild_analysis_cell())

    cells.append(md("---"))
    cells.append(md('''
## Reading a box plot

A box plot draws five numbers: the box spans the 25th to 75th percentile (the middle 50% of the data, the **interquartile range** or IQR), the line inside it is the median, the whiskers extend to the most extreme point within 1.5x the IQR, and anything beyond that is drawn as an individual dot - an **outlier** by this specific, computable definition, not a vague "unusually large value."
'''))
    cells.append(code('''
category_order = (analysis.groupby("category")["profit_ghs"].median()
                   .sort_values(ascending=False).index.tolist())
box_data = [analysis.loc[analysis["category"] == cat, "profit_ghs"].dropna() for cat in category_order]

fig, ax = plt.subplots(figsize=(10, 5))
bp = ax.boxplot(box_data, tick_labels=category_order, patch_artist=True,
                 flierprops={"markersize": 3, "markerfacecolor": MUTED, "markeredgecolor": "none"})
for patch in bp["boxes"]:
    patch.set_facecolor(PALETTE["blue"])
    patch.set_alpha(0.8)

ax.set_title("Cooking Oils has the highest median profit per order, and the widest spread")
ax.set_xlabel("Category")
ax.set_ylabel("Profit per order (GHS)")
ax.tick_params(axis="x", rotation=25)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
plt.show()

medians = analysis.groupby("category")["profit_ghs"].median().sort_values(ascending=False)
print(medians.round(2).to_string())
'''))
    cells.append(md('''
Sorting the categories by median (`category_order`, built before the plotting call) rather than alphabetically is deliberate - a reader scanning left to right sees the ranking immediately, the same reason the bar charts in 21b sort instead of defaulting to CSV order.
'''))

    cells.append(md("---"))
    cells.append(md('''
## A log-scale histogram, for the cases a linear one cannot show

The main lesson's revenue histogram worked because most orders cluster under GHS 400, with a long but visible tail. Unit price has the same right-skew problem in a more extreme form - a linear-scale histogram crams almost every order into the first few bins and leaves the rest of the axis empty.
'''))
    cells.append(code('''
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

axes[0].hist(analysis["unit_price_ghs"], bins=40, color=PALETTE["blue"], edgecolor="white")
axes[0].set_title("Linear scale: almost everything is invisible in one tall bin")
axes[0].set_xlabel("Unit price (GHS)")
axes[0].set_ylabel("Number of orders")

axes[1].hist(analysis["unit_price_ghs"], bins=np.logspace(
    np.log10(analysis["unit_price_ghs"].min()), np.log10(analysis["unit_price_ghs"].max()), 30),
    color=PALETTE["blue"], edgecolor="white")
axes[1].set_xscale("log")
axes[1].set_title("Log scale: the same data, readable across its full range")
axes[1].set_xlabel("Unit price (GHS, log scale)")
axes[1].set_ylabel("Number of orders")

fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
A log scale is the right call when a measure spans **orders of magnitude** (here, GHS 3.42 to GHS 495.28) and you care about relative differences across that whole range - never apply it by default, and always say so in the axis label (`"... (log scale)"`), because a reader who misses that note will misjudge every distance on the chart.
'''))

    cells.append(md('''
### Try It 4 - describe a distribution in words

Pick any one category and compute, for its `profit_ghs`: the median, the IQR, and the number of outliers by the 1.5x-IQR rule. Then write one sentence - with all three numbers in it - that you could put in a report without needing the chart next to it.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(footer_cell(
        "topic21_data_visualization.ipynb",
        "[21c - Change over time](topic21c_change_over_time.ipynb)",
        "[21e - Relationships](topic21e_relationships.ipynb)",
    ))
    return nb(cells)


# ---------------------------------------------------------------------------
# 21e - Relationships
# ---------------------------------------------------------------------------

def build_21e():
    cells = [opening_cell(
        "e", "Relationships",
        "The main lesson used one scatter plot and one correlation heatmap. This notebook adds a third variable to a scatter plot by colour and by size (a bubble chart), and uses a heatmap for a grid of category totals - not just correlation - to make the sequential-vs-diverging choice concrete.",
        "6",
    )]
    cells.append(setup_cell("data_visualization"))
    cells.append(rebuild_analysis_cell())

    cells.append(md("---"))
    cells.append(md('''
## A third variable, by colour

Quantity and revenue correlate at r = 0.41 overall. Colouring the same scatter by `segment` tests whether that relationship is the same for every kind of customer, or whether it is really three different relationships averaged together.
'''))
    cells.append(code('''
segment_order = ["Retail", "Wholesale", "Institution"]

fig, ax = plt.subplots(figsize=(8, 5.5))
for segment in segment_order:
    subset = analysis[analysis["segment"] == segment]
    r = subset["quantity"].corr(subset["revenue_ghs"])
    ax.scatter(subset["quantity"], subset["revenue_ghs"], s=20, alpha=0.5,
               color=SEGMENT_COLOR[segment], edgecolors="none",
               label=f"{segment} (r = {r:.2f})")

ax.set_title("Quantity predicts revenue best for Retail, worst for Institution")
ax.set_xlabel("Quantity ordered")
ax.set_ylabel("Order revenue (GHS)")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
This is the same idea as the zone-split line chart in 21c: an aggregate number (r = 0.41 for everyone) can average away real differences between groups. Colour by category here is doing identity work - telling the three segments apart - which is exactly the job categorical colour is for for, per the chart-selection rule.
'''))

    cells.append(md("---"))
    cells.append(md('''
## A third *numeric* variable, by size: the bubble chart

A bubble chart is a scatter plot where marker **size** encodes a third number. Here: population on the x-axis, revenue on the y-axis, and profit as the bubble size - three numbers about each region in one chart.
'''))
    cells.append(code('''
region_rev = analysis.groupby("region")["revenue_ghs"].sum()
region_profit = analysis.groupby("region")["profit_ghs"].sum()
regions_full = regions.set_index("region").join(region_rev.rename("revenue_ghs")).join(
    region_profit.rename("profit_ghs")).dropna()

fig, ax = plt.subplots(figsize=(9, 6))
sizes = regions_full["profit_ghs"] / regions_full["profit_ghs"].max() * 600 + 40
ax.scatter(regions_full["population_2021"], regions_full["revenue_ghs"],
           s=sizes, alpha=0.55, color=PALETTE["blue"], edgecolors="white", linewidth=0.8)

for standout in ["Greater Accra", "Ahafo"]:
    row = regions_full.loc[standout]
    ax.annotate(standout, xy=(row["population_2021"], row["revenue_ghs"]),
                xytext=(8, 8), textcoords="offset points", fontsize=9)

r = regions_full["population_2021"].corr(regions_full["revenue_ghs"])
ax.set_title(f"Population barely predicts revenue (r = {r:.2f}); bubble size is profit")
ax.set_xlabel("Population (2021 census)")
ax.set_ylabel("Revenue (GHS)")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
plt.show()

print("Greater Accra: population", f"{regions_full.loc['Greater Accra', 'population_2021']:,.0f}",
      "- revenue rank", int((regions_full['revenue_ghs'] > regions_full.loc['Greater Accra', 'revenue_ghs']).sum()) + 1, "of 16")
print("Ahafo: population", f"{regions_full.loc['Ahafo', 'population_2021']:,.0f}",
      "- revenue rank", int((regions_full['revenue_ghs'] > regions_full.loc['Ahafo', 'revenue_ghs']).sum()) + 1, "of 16")
'''))
    cells.append(md('''
Greater Accra is Ghana's most populous region by a wide margin and ranks only 10th of 16 by revenue; Ahafo has one of the smallest populations and ranks 2nd. That is the r = 0.05 from the main lesson's heatmap made concrete - population tells you almost nothing about which regions this business should prioritise, which is itself a useful, if negative, finding.

The size scaling (`sizes = ... / max * 600 + 40`) matters: without the `+ 40` floor, the smallest bubbles shrink to an invisible point, and without dividing by the maximum first, bubble sizes would not be comparable between charts with different profit scales.
'''))

    cells.append(md("---"))
    cells.append(md('''
## A heatmap for magnitude, not correlation

The main lesson's heatmap was diverging because correlation has a sign. A heatmap of revenue by zone and category has no sign - every cell is a non-negative amount of money - so it takes the **sequential** treatment: one hue, light to dark, more is simply more.
'''))
    cells.append(code('''
pivot = analysis.pivot_table(index="zone", columns="category", values="revenue_ghs", aggfunc="sum")
zone_order = ["Coastal", "Middle", "Northern"]
pivot = pivot.loc[zone_order]

fig, ax = plt.subplots(figsize=(10, 4))
im = ax.imshow(pivot.values, cmap="Blues", aspect="auto")
ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns, rotation=30, ha="right")
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index)
for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        value = pivot.values[i, j]
        ax.text(j, i, f"{value:,.0f}", ha="center", va="center",
                 color="white" if value > pivot.values.max() * 0.6 else INK, fontsize=8)
ax.set_title("Grains dominates revenue in every zone, most of all in Coastal")
fig.colorbar(im, ax=ax, shrink=0.85, label="Revenue (GHS)")
fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
Same chart type, two different colour rules, chosen by what the numbers mean - that is the point of the chart-selection rule's "colour job" column, not a coincidence of these two examples. A rainbow colormap (`"jet"`, `"rainbow"`) would pass as "more colourful" on either heatmap and be wrong on both: it has no natural zero, invents visual bands at arbitrary cutoffs, and is famously hard to read for anyone with colour-vision deficiency.
'''))

    cells.append(md('''
### Try It 5 - margin, not revenue

Build the same sequential heatmap, but of **profit margin** (`profit_ghs / revenue_ghs * 100`) by zone and category instead of raw revenue. Does the category that dominates *revenue* (Grains) also dominate *margin*? Answer in a comment, with the two numbers.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(footer_cell(
        "topic21_data_visualization.ipynb",
        "[21d - Distributions](topic21d_distributions.ipynb)",
        "[21f - Composition and seaborn](topic21f_composition_and_seaborn.ipynb)",
    ))
    return nb(cells)


# ---------------------------------------------------------------------------
# 21f - Composition and seaborn
# ---------------------------------------------------------------------------

def build_21f():
    cells = [opening_cell(
        "f", "Composition and seaborn",
        "The main lesson introduced pie and waffle charts as the narrow exception to the bar-chart default, and seaborn as a faster way to build charts you already know how to read. This notebook goes deeper on both: when a pie chart actively misleads, the waffle chart's print-friendly form, and seaborn's statistical plot types and theming.",
        "7 and 8",
    )]
    cells.append(setup_cell("data_visualization"))
    cells.append(rebuild_analysis_cell())

    cells.append(md("---"))
    cells.append(md('''
## When a pie chart actively misleads

The channel-mix pie in the main lesson was a defensible case: four slices, genuinely summing to a whole, with visibly different sizes. Here is the failure case - seven product categories, several of them close in size - built the same way.
'''))
    cells.append(code('''
category_share = (analysis.groupby("category")["revenue_ghs"].sum()
                   .pipe(lambda s: s / s.sum() * 100).sort_values(ascending=False))

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
axes[0].pie(category_share.values, labels=category_share.index, autopct="%1.0f%%",
            startangle=90, pctdistance=0.8,
            colors=[CATEGORY_COLOR[c] for c in category_share.index],
            wedgeprops={"edgecolor": "white", "linewidth": 1})
axes[0].set_title("Seven slices: can you rank Household vs Canned Goods vs Beverages by eye?")

bars = axes[1].barh(category_share.index[::-1], category_share.values[::-1],
                     color=[PALETTE["blue"] if c == category_share.index[0] else MUTED
                            for c in category_share.index[::-1]])
axes[1].bar_label(bars, fmt="%.0f%%", padding=3)
axes[1].set_title("The same seven categories, instantly ranked")
axes[1].set_xlabel("Share of 2023 revenue (%)")

fig.tight_layout()
plt.show()

print(category_share.round(1).to_string())
'''))
    cells.append(md('''
Household (9.0%), Canned Goods (7.6%), and Beverages (7.4%) are close enough in the pie that ranking them by slice angle alone is close to guessing. The bar chart ranks all seven correctly without the reader doing any work. This is the concrete version of the "≤5 categories" gate the main lesson stated - it is not an arbitrary number, it is the point past which slice angles stop being distinguishable at a glance.
'''))

    cells.append(md("---"))
    cells.append(md('''
## The waffle chart, and its one real advantage

A waffle chart trades the pie's one visual advantage (a single, instantly-recognised "whole") for a grid that is easier to read precisely - counting squares is more accurate than judging an angle - and, built with hatch patterns instead of fill colour, it is the one composition chart in this lesson that survives being printed in black and white or viewed by a reader with colour-vision deficiency.
'''))
    cells.append(code('''
channel_share = (analysis.groupby("channel")["revenue_ghs"].sum()
                  .pipe(lambda s: (s / s.sum() * 100).round(0).astype(int))
                  .sort_values(ascending=False))
channel_share.iloc[0] += 100 - channel_share.sum()  # rounding to exactly 100 squares

hatches = ["///", "...", "xxx", "\\\\\\\\\\\\"]
fig, ax = plt.subplots(figsize=(6.5, 6.5))
rows, cols = 10, 10
square = 0
for (label, pct), hatch in zip(channel_share.items(), hatches):
    for _ in range(pct):
        r, c = divmod(square, cols)
        ax.add_patch(plt.Rectangle((c, rows - 1 - r), 1, 1, facecolor="white",
                                    edgecolor="black", hatch=hatch, linewidth=0.6))
        square += 1

handles = [plt.Rectangle((0, 0), 1, 1, facecolor="white", edgecolor="black", hatch=h) for h in hatches]
ax.legend(handles, [f"{label} ({pct}%)" for label, pct in channel_share.items()],
          loc="upper center", bbox_to_anchor=(0.5, -0.05), ncol=2, frameon=False)
ax.set_xlim(0, cols)
ax.set_ylim(0, rows)
ax.set_aspect("equal")
ax.set_xticks([])
ax.set_yticks([])
ax.set_title("2023 revenue share by channel, one square per percentage point")
fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
The rounding correction (`channel_share.iloc[0] += 100 - channel_share.sum()`) exists because rounding four percentages independently will not reliably sum to exactly 100 - without it, the grid comes up one square short or one square long, which is a worse failure for a waffle chart than it would be for almost any other chart type, because "100 squares" is the entire premise.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Seaborn: theming and statistical plot types

`sns.set_theme()` changes matplotlib's global defaults - grid style, font scale, colour cycle - for every chart built afterwards in the same session. This course sets its own grid and spine style in every notebook's setup cell, so calling `sns.set_theme()` carelessly can silently undo it. Pass `rc=` to layer seaborn's theme on top of this course's choices instead of replacing them.
'''))
    cells.append(code('''
import seaborn as sns

sns.set_theme(style="white", rc={
    "axes.edgecolor": "#c3c2b7", "grid.color": "#e1e0d9", "axes.grid": True,
})
segment_order = ["Retail", "Wholesale", "Institution"]

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

sns.histplot(data=analysis, x="revenue_ghs", bins=40, color=PALETTE["blue"], ax=axes[0])
axes[0].set_title("sns.histplot: same chart as the main lesson's histogram, one line")
axes[0].set_xlabel("Order revenue (GHS)")

sns.boxplot(data=analysis, x="segment", y="profit_ghs", order=segment_order,
            hue="segment", palette=SEGMENT_COLOR, legend=False, ax=axes[1])
axes[1].set_title("sns.boxplot: built-in grouping by category")
axes[1].set_xlabel("Segment")
axes[1].set_ylabel("Profit per order (GHS)")

fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
`hue="segment", palette=SEGMENT_COLOR, legend=False` is the pattern for keeping this course's fixed colour assignment inside a seaborn call that would otherwise pick its own palette - `palette=` accepts the same dict you have been building bar and line charts from all topic. Seaborn saves the most code on exactly the plots that need grouping, a fitted statistic, or both - a plain single-series bar or line is often no shorter in seaborn than in matplotlib, which is why the main lesson still reaches for matplotlib directly most of the time.
'''))

    cells.append(md('''
### Try It 6 - a seaborn panel

Using seaborn, build a 1x2 figure: left panel `sns.scatterplot` of quantity vs revenue coloured by segment (use `hue="segment", palette=SEGMENT_COLOR`); right panel `sns.barplot` of average order value (`revenue_ghs`) by channel, coloured with `color=PALETTE["blue"]`. Give both panels a title that states a finding.
'''))
    cells.append(code("segment_order = [\"Retail\", \"Wholesale\", \"Institution\"]\n# YOUR CODE HERE"))

    cells.append(footer_cell(
        "topic21_data_visualization.ipynb",
        "[21e - Relationships](topic21e_relationships.ipynb)",
        "[21g - Visualization practice](topic21g_visualization_practice.ipynb)",
    ))
    return nb(cells)


# ---------------------------------------------------------------------------
# 21g - Visualization practice (pure consolidation, no new teaching)
# ---------------------------------------------------------------------------

def build_21g():
    cells = [md('''
# Topic 21g - Visualization practice

A consolidation notebook. Everything here uses the whole Topic 21 toolkit and gives you no worked answers - only the checks that tell you whether your answer is right.

Work through the [main lesson](topic21_data_visualization.ipynb) and notebooks 21a to 21f first.

## The scenario

The managing director is opening next week's board meeting with five charts and nothing else - no code, no tables, just the pictures. She has asked you for:

1. Which **segment** is the most profitable, and by how much?
2. Did the **number of orders** grow steadily through 2023, or in bursts?
3. Which **product category** has the widest spread of unit prices - and does that line up with the return-rate problem you already know about from Topic 20?
4. Which **day-and-channel combination** is busiest, and which is quietest?
5. How concentrated is profit among the best customers - does it matter that a third of customers are "Gold" tier if that tier holds nearly all the profit?

Every one of these is a different chart type for a reason - use the chart-selection rule from the main lesson to pick each one.
''')]
    cells.append(setup_cell("data_visualization"))
    cells.append(rebuild_analysis_cell())
    cells.append(code('''
import seaborn as sns

charts_dir = Path("charts")
charts_dir.mkdir(exist_ok=True)
print("Analysis table ready:", analysis.shape)
'''))

    cells.append(md("---"))
    cells.append(md('''
## Task 1 - Profit by segment

Build a sorted bar chart of total profit by segment, with the top segment emphasised in the course blue and the others in grey. Title it with the finding, label both axes, and add value labels on the bars.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(md('''
## Task 2 - Orders over time

Build a line chart of the **number of orders per month** in 2023 (not revenue), with a 3-month rolling average overlaid in the course blue and the raw monthly line in grey. Title it with the finding.

Look carefully at the raw line before you title the chart: find the single busiest month using `.idxmax()`, then check whether any other month ties it. A title that says "busiest month was X" when two months are tied is wrong, even if the code that produced it ran without error.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(md('''
## Task 3 - Distribution of unit price by category

Build a box plot of `unit_price_ghs` by category, sorted by median. Identify the category with the highest median unit price, and in a markdown cell below, connect it to a fact from Topic 20: that category's return rate.
'''))
    cells.append(code("# YOUR CODE HERE"))
    cells.append(md('''
**Is the category with the highest unit price also the category with the highest return rate? Write the connection, with both numbers.**

*(Write your answer here.)*
'''))

    cells.append(md('''
## Task 4 - Busiest day and channel

Build a sequential heatmap of order **count** by weekday (rows) and channel (columns). Use one hue, light to dark - this is a magnitude grid, not a correlation, so it does not get the diverging treatment from the main lesson's correlation heatmap. Annotate each cell with its count.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(md('''
## Task 5 - Profit concentration among customers

Using `pd.qcut`, split customers into three profit tiers - `Bronze`, `Silver`, `Gold` - exactly as Topic 20g did. Compute each tier's share of total profit, and build **one** chart of your choice (bar or pie) to show it. Justify your choice in a one-line comment: is this a case where a pie chart is defensible, by the rule from 21f?
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(md("---"))
    cells.append(md('''
## Task 6 - The board page

Assemble Tasks 1, 2, 3, 4, and 5 into a single Figure with `plt.subplots(2, 3)` (five panels used, one left blank or holding a title/summary), save it to `charts/board_dashboard.png` at 150 dpi, and display it.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(md('''
## Self-check

- [ ] Task 1: the most profitable segment is Retail, at GHS 33,442.04
- [ ] Task 2: August and November are **tied** for the busiest month, at 115 orders each - your title does not claim a single busiest month unless it checked for ties
- [ ] Task 3: Cooking Oils has the highest median unit price (GHS 76.33), and it is also the category with the highest return rate (16.5%) from Topic 20
- [ ] Task 4: Shop on Thursday is the single busiest weekday-channel combination, at 90 orders
- [ ] Task 5: Gold-tier customers (the top third by profit) hold 69.2% of all profit, despite being only a third of customers
- [ ] Every chart has a title that states a finding, axis labels with units, and - where there is more than one series - a legend
- [ ] No `# YOUR CODE HERE` remains anywhere
- [ ] The board dashboard is saved to `charts/board_dashboard.png`

---
## Where this fits

- [Back to the main lesson](topic21_data_visualization.ipynb)
- Previous: [21f - Composition and seaborn](topic21f_composition_and_seaborn.ipynb)
- Next: [Topic 21 assignment](assignments/topic21_assignment_trading_dashboard.ipynb)
'''))
    return nb(cells)


# ---------------------------------------------------------------------------
# Assignment + instructor solutions: shared text and check cells
# ---------------------------------------------------------------------------

ASSIGNMENT_TITLE = "# Topic 21 Assignment - The Director's Dashboard"

ASSIGNMENT_SCENARIO = '''
## Scenario

You are still the Ghanaian retail distributor's analyst from Topic 20. The managing director read your 2023 Trading Review and had one response: "I cannot bring a DataFrame into a board meeting. Give me a page of charts."

Your job this time is not to find new numbers - every number you need, you already found in Topic 20. Your job is to turn five of those findings into five charts, each one built to the standard this topic set: a title that states the finding, axes labelled with units, a legend when there is more than one series, and the right chart type for the question, not the first one you thought of.

### What you are practising

| Skill | Where |
|---|---|
| Choosing a chart type from the question, not habit | Part 1 |
| Bar charts with emphasis, sorted, labelled | Part 3 |
| Line charts with a rolling average | Part 4 |
| Box plots and reading a distribution | Part 5 |
| A sequential heatmap for a count grid | Part 6 |
| Composition charts, used only when justified | Part 7 |
| Assembling a multi-panel dashboard | Part 8 |
| Checking a chart's structure in code, not just by eye | Every check cell |
| Submitting work with Git and GitHub | Part 11 |
'''

ASSIGNMENT_SUBMIT = '''
## What you must submit

A **public** GitHub repository named **`itfy-data-visualization`** containing:

1. this notebook, completed, **run from top to bottom so every output is visible**;
2. `data/` - the six source CSVs, unchanged;
3. `charts/` - at least six saved PNGs: one bar, one line, one distribution, one relationship or heatmap, one composition chart, and the final dashboard;
4. `charts/captions.json` - one entry per saved chart, with its chart type and the finding it shows;
5. `README.md` - your findings, written for the managing director, with the dashboard image embedded.

Full submission instructions, written for Windows with no assumed knowledge, are in [the GitHub submission guide](../../data_analysis_process/topic19d_appendix_submitting_with_github.ipynb). You have now done this twice.

### Rules

- **Complete every function skeleton.** Loose code in a cell instead of a completed function loses that part's marks.
- **Every chart needs a title that states a finding, axis labels with units, and a legend if it has more than one series.** The check cells test this in code - they will tell you if a chart is missing one.
- **At most one composition chart (pie or waffle), and only for five categories or fewer that genuinely sum to a whole.** Justify your choice of pie, waffle, or bar in the one line Part 7 asks for.
- **Never a dual-axis chart.** If two measures do not share a scale, that is two charts.
- **One series, one colour**, unless colour is telling series apart or marking the one bar or line that is the finding.
- **Never modify the files in `data/`.**
'''

ASSIGNMENT_HOWTO = '''
## How to work through this notebook

Replace every `# TODO n` with your code, and delete each `raise NotImplementedError(...)` once the function works. The check cell beneath each part tells you whether your answer is right - it compares against figures and chart properties that are known to be correct, so a `False` means your code, not the check, is wrong.

Work in order. Every part uses the `analysis` table built in Part 2.
'''

PART1_MD = '''
## Part 1 - Chart-selection memo

Before building anything, decide the chart type for each of the director's five questions, and say why in one line each, using the chart-selection rule from the main lesson.

1. Which segment is the most profitable?
2. Did order volume grow steadily through 2023, or in bursts?
3. Which category has the widest spread of unit prices?
4. Which day-and-channel combination is busiest?
5. How concentrated is profit among the best customers?
'''

PART1_ANSWER_MD = '''
**Your chart-selection memo:**

1. *(chart type and one-line reason)*
2. *(chart type and one-line reason)*
3. *(chart type and one-line reason)*
4. *(chart type and one-line reason)*
5. *(chart type and one-line reason)*
'''

PART2_MD = '''
---
## Part 2 - Rebuild the analysis table

Paste the function you built in Topic 20. This is the same contract: five raw tables in, one analysis-ready table out.
'''

CHECK2 = '''
# Check cell. All five must print True.
print("rows:            ", len(analysis) == 1200)
print("orphans:         ", analysis["region"].isna().sum() == 27)
print("returned:        ", analysis["was_returned"].sum() == 96)
print("total revenue:   ", round(analysis["revenue_ghs"].sum(), 2) == 230001.08)
print("total profit:    ", round(analysis["profit_ghs"].sum(), 2) == 65886.38)
'''

PART3_MD = '''
---
## Part 3 - Bar chart: profit by segment

Write `plot_profit_by_segment(analysis)`, returning `(fig, ax)`. It must:

- show total profit by segment, sorted highest to lowest;
- colour the top segment's bar in `PALETTE["blue"]` and every other bar in `MUTED`;
- add a value label on each bar;
- set a title that states which segment is most profitable and by how much;
- label both axes, with units on the y-axis.
'''

PART3_TODO = '''
def plot_profit_by_segment(analysis):
    """Bar chart of total profit by segment, sorted, with the leader emphasised."""
    # TODO 1: group by segment, sum profit_ghs, sort descending.
    # TODO 2: build the fig/ax, colour the top bar PALETTE["blue"], the rest MUTED.
    # TODO 3: bar_label, title (state the finding), xlabel, ylabel (with units).
    raise NotImplementedError("Complete this function, then delete this line.")
'''

PART3_SOLUTION = '''
def plot_profit_by_segment(analysis):
    """Bar chart of total profit by segment, sorted, with the leader emphasised."""
    profit = analysis.groupby("segment")["profit_ghs"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = [PALETTE["blue"] if seg == profit.index[0] else MUTED for seg in profit.index]
    bars = ax.bar(profit.index, profit.values, color=colors)
    ax.bar_label(bars, fmt="GHS %.0f", padding=3)
    ax.set_title(f"{profit.index[0]} is the most profitable segment, at GHS {profit.values[0]:,.0f}")
    ax.set_xlabel("Segment")
    ax.set_ylabel("Profit (GHS)")
    return fig, ax
'''

CHECK3 = '''
# Check cell. All must print True.
fig3, ax3 = plot_profit_by_segment(analysis)
heights = [p.get_height() for p in ax3.patches]
print("3 bars:          ", len(ax3.patches) == 3)
print("sorted desc:     ", heights == sorted(heights, reverse=True))
print("values correct:  ", [round(h, 2) for h in heights] == [33442.04, 25842.35, 4244.12])
print("top bar is blue: ", matplotlib.colors.to_hex(ax3.patches[0].get_facecolor()) == PALETTE["blue"])
print("title present:   ", len(ax3.get_title()) > 10)
print("ylabel has units:", "GHS" in ax3.get_ylabel())
plt.show()
'''

PART4_MD = '''
---
## Part 4 - Line chart: order volume over time

Write `plot_monthly_order_count(analysis)`, returning `(fig, ax)`. It must:

- plot the **number of orders per month** (not revenue) for 2023, in `MUTED`, with markers;
- overlay a 3-month rolling average in `PALETTE["blue"]`;
- include a legend naming both lines;
- set a title - check carefully whether one month or two months share the peak before you word it.
'''

PART4_TODO = '''
def plot_monthly_order_count(analysis):
    """Line chart of monthly order count, with a 3-month rolling average."""
    # TODO 4: group by month, use .size() for order COUNT, not revenue.
    # TODO 5: plot the raw monthly line (MUTED) and the rolling(3).mean() line (PALETTE["blue"]).
    # TODO 6: legend, title (check for ties in the peak month first), axis labels.
    raise NotImplementedError("Complete this function, then delete this line.")
'''

PART4_SOLUTION = '''
def plot_monthly_order_count(analysis):
    """Line chart of monthly order count, with a 3-month rolling average."""
    monthly = analysis.groupby(analysis["order_date"].dt.to_period("M")).size()
    monthly.index = monthly.index.astype(str)
    rolling = monthly.rolling(3).mean()
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(monthly.index, monthly.values, color=MUTED, marker="o", markersize=4,
            linewidth=1.5, label="Monthly orders")
    ax.plot(monthly.index, rolling.values, color=PALETTE["blue"], linewidth=2.5,
            label="3-month average")
    ax.set_title("Order volume peaked in August and November 2023 (115 orders each)")
    ax.set_xlabel("Month of 2023")
    ax.set_ylabel("Number of orders")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(frameon=False)
    return fig, ax
'''

CHECK4 = '''
# Check cell. All must print True.
fig4, ax4 = plot_monthly_order_count(analysis)
print("2 lines:         ", len(ax4.lines) == 2)
print("legend present:  ", ax4.get_legend() is not None)
print("title present:   ", len(ax4.get_title()) > 10)
plt.show()
'''

PART5_MD = '''
---
## Part 5 - Box plot: unit price by category

Write `plot_unit_price_distribution(analysis)`, returning `(fig, ax)`. It must:

- show a box plot of `unit_price_ghs` for every category, ordered by median (highest first);
- use `patch_artist=True` so the boxes can be coloured `PALETTE["blue"]`;
- set a title naming the category with the highest median.
'''

PART5_TODO = '''
def plot_unit_price_distribution(analysis):
    """Box plot of unit price by category, sorted by median, highest first."""
    # TODO 7: compute the category order by median unit_price_ghs, descending.
    # TODO 8: build one list of Series (one per category, in that order) for ax.boxplot.
    # TODO 9: patch_artist=True, colour boxes PALETTE["blue"], title, axis labels.
    raise NotImplementedError("Complete this function, then delete this line.")
'''

PART5_SOLUTION = '''
def plot_unit_price_distribution(analysis):
    """Box plot of unit price by category, sorted by median, highest first."""
    order = (analysis.groupby("category")["unit_price_ghs"].median()
             .sort_values(ascending=False).index.tolist())
    data = [analysis.loc[analysis["category"] == c, "unit_price_ghs"].dropna() for c in order]
    fig, ax = plt.subplots(figsize=(10, 5))
    bp = ax.boxplot(data, tick_labels=order, patch_artist=True,
                     flierprops={"markersize": 3, "markerfacecolor": MUTED, "markeredgecolor": "none"})
    for patch in bp["boxes"]:
        patch.set_facecolor(PALETTE["blue"])
        patch.set_alpha(0.8)
    ax.set_title("Cooking Oils has the highest median unit price of any category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Unit price (GHS)")
    ax.tick_params(axis="x", rotation=25)
    return fig, ax
'''

CHECK5 = '''
# Check cell. All must print True.
fig5, ax5 = plot_unit_price_distribution(analysis)
print("7 box patches:   ", len(ax5.patches) == 7)
print("title present:   ", len(ax5.get_title()) > 10)
plt.show()
'''

PART6_MD = '''
---
## Part 6 - Heatmap: busiest day and channel

Write `plot_order_heatmap(analysis)`, returning `(fig, ax, grid)` where `grid` is the weekday-by-channel order-count DataFrame. It must:

- use `ax.imshow` with a **sequential** colormap (`"Blues"`) - this is a count, not a correlation, so it does not get the diverging treatment;
- order weekdays Monday to Sunday, and channels in a fixed order;
- annotate each cell with its count;
- set a title naming the single busiest day-and-channel combination.
'''

PART6_TODO = '''
def plot_order_heatmap(analysis):
    """Sequential heatmap of order count by weekday and channel."""
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    channel_order = ["Field Agent", "Online", "Phone", "Shop"]
    # TODO 10: build `grid` - a weekday x channel order-count table, reindexed to those orders.
    # TODO 11: ax.imshow(grid.values, cmap="Blues", ...), tick labels, text annotation per cell.
    # TODO 12: title naming the busiest combination, colorbar.
    raise NotImplementedError("Complete this function, then delete this line.")
'''

PART6_SOLUTION = '''
def plot_order_heatmap(analysis):
    """Sequential heatmap of order count by weekday and channel."""
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    channel_order = ["Field Agent", "Online", "Phone", "Shop"]
    grid = (analysis.groupby(["weekday", "channel"]).size()
            .unstack().reindex(weekday_order)[channel_order])
    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(grid.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(channel_order)))
    ax.set_xticklabels(channel_order)
    ax.set_yticks(range(len(weekday_order)))
    ax.set_yticklabels(weekday_order)
    for i in range(len(weekday_order)):
        for j in range(len(channel_order)):
            ax.text(j, i, int(grid.values[i, j]), ha="center", va="center", fontsize=8)
    ax.set_title("Shop on Thursday is the single busiest day-and-channel combination")
    fig.colorbar(im, ax=ax, shrink=0.85, label="Number of orders")
    return fig, ax, grid
'''

CHECK6 = '''
# Check cell. All must print True.
fig6, ax6, grid6 = plot_order_heatmap(analysis)
print("one image:       ", len(ax6.get_images()) == 1)
print("shape 7x4:       ", grid6.shape == (7, 4))
busiest = grid6.stack().idxmax()
print("busiest is Shop/Thursday, 90:", busiest == ("Thursday", "Shop") and grid6.stack().max() == 90)
plt.show()
'''

PART7_MD = '''
---
## Part 7 - Composition: customer tiers

Write `plot_customer_tier_composition(analysis)`, returning `(fig, ax, tier_share, composition_justification)`. It must:

- split customers into `Bronze`, `Silver`, `Gold` tiers by total profit with `pd.qcut(..., 3, ...)`, exactly as Topic 20 did;
- compute each tier's share of total profit as `tier_share` (a Series indexed Bronze, Silver, Gold);
- build **either** a bar or a pie chart of `tier_share` - your choice;
- set `composition_justification` to a one-line string explaining why you chose that chart type over the other, using the rule from 21f.
'''

PART7_TODO = '''
def plot_customer_tier_composition(analysis):
    """Composition chart of profit share by customer tier (Bronze/Silver/Gold)."""
    # TODO 13: per-customer total profit, then pd.qcut into 3 tiers.
    # TODO 14: tier_share - each tier's % share of total profit, indexed Bronze/Silver/Gold.
    # TODO 15: build a bar OR pie chart of tier_share; title states the leading tier's share.
    # TODO 16: composition_justification - one line, referencing the 21f rule.
    raise NotImplementedError("Complete this function, then delete this line.")
'''

PART7_SOLUTION = '''
def plot_customer_tier_composition(analysis):
    """Composition chart of profit share by customer tier (Bronze/Silver/Gold)."""
    cust_profit = analysis.groupby("customer_id")["profit_ghs"].sum()
    tiers = pd.qcut(cust_profit, 3, labels=["Bronze", "Silver", "Gold"])
    tier_share = (cust_profit.groupby(tiers, observed=True).sum()
                  .pipe(lambda s: (s / s.sum() * 100).round(1))
                  .reindex(["Bronze", "Silver", "Gold"]))

    composition_justification = (
        "A bar chart: 3 categories is within the pie-chart limit, but Gold vs Silver "
        "(69.2% vs 22.3%) is still easier to compare as bar length than as slice angle."
    )
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = [PALETTE["blue"] if t == "Gold" else MUTED for t in tier_share.index]
    bars = ax.bar(tier_share.index, tier_share.values, color=colors)
    ax.bar_label(bars, fmt="%.1f%%", padding=3)
    ax.set_title("Gold-tier customers hold 69.2% of all profit")
    ax.set_xlabel("Customer tier")
    ax.set_ylabel("Share of total profit (%)")
    return fig, ax, tier_share, composition_justification
'''

CHECK7 = '''
# Check cell. All must print True.
fig7, ax7, tier_share7, justification7 = plot_customer_tier_composition(analysis)
print("3 tiers:         ", len(tier_share7) == 3)
print("shares correct:  ", tier_share7.to_dict() == {"Bronze": 8.5, "Silver": 22.3, "Gold": 69.2})
print("justified:       ", len(justification7) > 20)
plt.show()
'''

PART8_MD = '''
---
## Part 8 - The dashboard

Write `build_dashboard(analysis, charts_dir)`, which builds one Figure with `plt.subplots(2, 3)` containing all five charts above (one panel may hold a title/summary instead of a sixth chart), saves it to `charts_dir / "director_dashboard.png"` at 150 dpi, and returns the saved path.
'''

PART8_TODO = '''
def build_dashboard(analysis, charts_dir):
    """Assemble Parts 3-7 into one 2x3 dashboard figure, saved to disk."""
    # TODO 17: plt.subplots(2, 3, ...), one panel per chart above (5 charts, 1 spare panel).
    # TODO 18: give the figure an overall title with fig.suptitle(...).
    # TODO 19: charts_dir.mkdir(exist_ok=True); fig.savefig(..., dpi=150, bbox_inches="tight").
    raise NotImplementedError("Complete this function, then delete this line.")
'''

PART8_SOLUTION = '''
def build_dashboard(analysis, charts_dir):
    """Assemble Parts 3-7 into one 2x3 dashboard figure, saved to disk."""
    charts_dir.mkdir(exist_ok=True)
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))

    profit = analysis.groupby("segment")["profit_ghs"].sum().sort_values(ascending=False)
    colors = [PALETTE["blue"] if s == profit.index[0] else MUTED for s in profit.index]
    axes[0, 0].bar(profit.index, profit.values, color=colors)
    axes[0, 0].set_title("Retail is the most profitable segment")
    axes[0, 0].set_ylabel("Profit (GHS)")

    monthly = analysis.groupby(analysis["order_date"].dt.to_period("M")).size()
    monthly.index = monthly.index.astype(str)
    axes[0, 1].plot(monthly.index, monthly.values, color=PALETTE["blue"], marker="o")
    axes[0, 1].set_title("Orders peaked in Aug and Nov")
    axes[0, 1].set_ylabel("Number of orders")
    axes[0, 1].tick_params(axis="x", rotation=45, labelsize=7)

    order = (analysis.groupby("category")["unit_price_ghs"].median()
             .sort_values(ascending=False).index.tolist())
    data = [analysis.loc[analysis["category"] == c, "unit_price_ghs"].dropna() for c in order]
    axes[0, 2].boxplot(data, tick_labels=order)
    axes[0, 2].set_title("Cooking Oils: widest, highest unit price")
    axes[0, 2].set_ylabel("Unit price (GHS)")
    axes[0, 2].tick_params(axis="x", rotation=60, labelsize=6)

    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    channel_order = ["Field Agent", "Online", "Phone", "Shop"]
    grid = (analysis.groupby(["weekday", "channel"]).size()
            .unstack().reindex(weekday_order)[channel_order])
    im = axes[1, 0].imshow(grid.values, cmap="Blues", aspect="auto")
    axes[1, 0].set_xticks(range(len(channel_order)))
    axes[1, 0].set_xticklabels(channel_order, rotation=30, ha="right", fontsize=7)
    axes[1, 0].set_yticks(range(len(weekday_order)))
    axes[1, 0].set_yticklabels(weekday_order, fontsize=7)
    axes[1, 0].set_title("Shop + Thursday is busiest")
    fig.colorbar(im, ax=axes[1, 0], shrink=0.85, label="Orders")

    cust_profit = analysis.groupby("customer_id")["profit_ghs"].sum()
    tiers = pd.qcut(cust_profit, 3, labels=["Bronze", "Silver", "Gold"])
    tier_share = (cust_profit.groupby(tiers, observed=True).sum()
                  .pipe(lambda s: s / s.sum() * 100).reindex(["Bronze", "Silver", "Gold"]))
    axes[1, 1].bar(tier_share.index, tier_share.values, color=PALETTE["blue"])
    axes[1, 1].set_title("Gold holds 69.2% of profit")
    axes[1, 1].set_ylabel("Share of total profit (%)")

    axes[1, 2].axis("off")
    axes[1, 2].text(0.5, 0.5, "2023 Trading Review\\nBoard summary", ha="center", va="center", fontsize=13)

    fig.suptitle("2023 Trading Review - board summary", fontsize=15)
    fig.tight_layout()
    out_path = charts_dir / "director_dashboard.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    return out_path
'''

CHECK8 = '''
# Check cell. Must print True.
charts_dir = Path("charts")
dashboard_path = build_dashboard(analysis, charts_dir)
print("dashboard saved: ", dashboard_path.exists() and dashboard_path.stat().st_size > 0)
plt.show()
'''

PART9_MD = '''
---
## Part 9 - Captions manifest

Write `build_captions(charts_dir)`, which writes `charts_dir / "captions.json"` - a JSON list with one object per PNG in `charts_dir`, each with `"file"`, `"chart_type"`, and `"finding"` keys - and returns the path it wrote to. Save the five individual charts from Parts 3-7 to `charts_dir` first (each with `fig.savefig(...)`), in addition to the dashboard Part 8 already saved.
'''

PART9_TODO = '''
def build_captions(charts_dir):
    """Write charts/captions.json: one entry per saved PNG, describing its finding."""
    # TODO 20: save each of the five Part 3-7 figures to charts_dir (if not done already).
    # TODO 21: build a list of {"file": ..., "chart_type": ..., "finding": ...} dicts.
    # TODO 22: json.dump the list to charts_dir / "captions.json"; return that path.
    raise NotImplementedError("Complete this function, then delete this line.")
'''

PART9_SOLUTION = '''
def build_captions(charts_dir):
    """Write charts/captions.json: one entry per saved PNG, describing its finding."""
    fig3.savefig(charts_dir / "profit_by_segment.png", dpi=150, bbox_inches="tight")
    fig4.savefig(charts_dir / "monthly_order_count.png", dpi=150, bbox_inches="tight")
    fig5.savefig(charts_dir / "unit_price_distribution.png", dpi=150, bbox_inches="tight")
    fig6.savefig(charts_dir / "order_heatmap.png", dpi=150, bbox_inches="tight")
    fig7.savefig(charts_dir / "customer_tier_composition.png", dpi=150, bbox_inches="tight")

    captions = [
        {"file": "profit_by_segment.png", "chart_type": "bar",
         "finding": "Retail is the most profitable segment, at GHS 33,442.04."},
        {"file": "monthly_order_count.png", "chart_type": "line",
         "finding": "Order volume peaked in August and November 2023, at 115 orders each."},
        {"file": "unit_price_distribution.png", "chart_type": "box",
         "finding": "Cooking Oils has the highest median unit price of any category."},
        {"file": "order_heatmap.png", "chart_type": "heatmap",
         "finding": "Shop on Thursday is the single busiest day-and-channel combination."},
        {"file": "customer_tier_composition.png", "chart_type": "bar",
         "finding": "Gold-tier customers hold 69.2% of all profit."},
        {"file": "director_dashboard.png", "chart_type": "dashboard",
         "finding": "The 2023 Trading Review, as five findings on one page."},
    ]
    out_path = charts_dir / "captions.json"
    with open(out_path, "w") as f:
        json.dump(captions, f, indent=2)
    return out_path
'''

CHECK9 = '''
# Check cell. All must print True.
captions_path = build_captions(charts_dir)
with open(captions_path) as f:
    captions = json.load(f)
print("captions.json written:", captions_path.exists())
print("6 entries:            ", len(captions) == 6)
print("all keys present:     ", all({"file", "chart_type", "finding"} <= set(c.keys()) for c in captions))
'''

PART10_MD = '''
---
### Your findings

**1. Headline for the board:**

*(Write your answer here.)*

**2. The one chart you expect the most questions about, and why:**

*(Write your answer here.)*

**3. Which composition-chart choice you made in Part 7, and why the other option would have been worse here:**

*(Write your answer here.)*

**4. Two limitations of this dashboard:**

1. *(Write your answer here.)*
2. *(Write your answer here.)*

**5. What chart you would add next, and what question it would answer:**

*(Write your answer here.)*
'''

RUBRIC_MD = '''
---
## Marking rubric

| Area | What earns the marks | Marks |
|---|---:|---:|
| Chart-selection memo | All five chart types correctly matched to the question, with a real reason each | 10 |
| Analysis table rebuilt | All five checks pass | 8 |
| Bar chart (Part 3) | Sorted, emphasis colour correct, value labels, title states the finding, units on y-axis | 12 |
| Line chart (Part 4) | Correct measure (count, not revenue), rolling average, legend, title accounts for the tie | 12 |
| Box plot (Part 5) | Sorted by median, 7 categories, correctly coloured, title names the leader | 10 |
| Heatmap (Part 6) | Sequential colormap, correct orientation and order, annotated, title names the busiest cell | 12 |
| Composition chart (Part 7) | Correct tier shares, a real justification for bar vs pie, title states the leading tier's share | 12 |
| Dashboard (Part 8) | All five findings present in one figure, saved correctly | 10 |
| Captions manifest (Part 9) | Valid JSON, one entry per chart, each finding stated in words | 8 |
| Findings and limitations | Numbers in every claim; the composition justification is defended, not just repeated | 10 |
| Repository, README, commits | Public repo, correct structure, README written for the director, dashboard embedded | 10 |
| **Total** | | **114** |

Marks are lost for: any chart missing a title, axis units, or a legend where one is needed; a composition chart used for more than five categories or without a stated justification; a dual-axis chart anywhere; `NotImplementedError` left in any function; and a repository that is not public.
'''

REFERENCES_MD = '''
## References

### Topic 21 material
- [Main lesson - Topic 21 Data Visualization](../topic21_data_visualization.ipynb)
- [21a - Anatomy of a chart](../topic21a_anatomy_of_a_chart.ipynb)
- [21b - Comparing categories](../topic21b_comparing_categories.ipynb)
- [21c - Change over time](../topic21c_change_over_time.ipynb)
- [21d - Distributions](../topic21d_distributions.ipynb)
- [21e - Relationships](../topic21e_relationships.ipynb)
- [21f - Composition and seaborn](../topic21f_composition_and_seaborn.ipynb)
- [21g - Visualization practice](../topic21g_visualization_practice.ipynb)

### matplotlib and seaborn documentation
- [matplotlib: Quick start guide](https://matplotlib.org/stable/users/explain/quick_start.html)
- [matplotlib: Choosing colormaps](https://matplotlib.org/stable/users/explain/colors/colormaps.html)
- [seaborn: An introduction](https://seaborn.pydata.org/tutorial/introduction.html)

### Elsewhere in the course
- [Topic 20 - Data wrangling](../../data_wrangling/topic20_data_wrangling.ipynb)
- [Submitting your work with GitHub](../../data_analysis_process/topic19d_appendix_submitting_with_github.ipynb)
'''


def build_assignment():
    cells = [md(ASSIGNMENT_TITLE + "\n" + ASSIGNMENT_SCENARIO)]
    cells.append(md(ASSIGNMENT_SUBMIT))
    cells.append(md(ASSIGNMENT_HOWTO))
    cells.append(md("---"))
    cells.append(code('''
# Run this cell as it is. Do not change it.
from pathlib import Path
import json

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

PALETTE = {
    "blue": "#2a78d6", "aqua": "#1baf7a", "yellow": "#eda100", "green": "#008300",
    "violet": "#4a3aa7", "red": "#e34948", "magenta": "#e87ba4", "orange": "#eb6834",
}
MUTED = "#c3c2b7"
INK = "#0b0b0b"


def find_data_dir():
    candidates = [Path.cwd() / "data", Path.cwd() / "data_visualization" / "data",
                  Path.cwd().parent / "data"]
    for candidate in candidates:
        if (candidate / "orders.csv").exists():
            return candidate
    raise FileNotFoundError("Could not find orders.csv. Looked in: " +
                             ", ".join(str(c) for c in candidates))


DATA_DIR = find_data_dir()
pd.set_option("display.max_columns", 30)
plt.rcParams["figure.dpi"] = 110
print("data folder:", DATA_DIR)
'''))

    cells.append(md(PART1_MD))
    cells.append(md(PART1_ANSWER_MD))

    cells.append(md(PART2_MD))
    cells.append(code('''
def clean_region(series):
    # TODO 0a: strip whitespace, collapse repeated spaces, title-case.
    raise NotImplementedError("Complete this function, then delete this line.")


def build_analysis_table(orders, customers, products, regions, returns):
    """Combine the five raw tables into one analysis-ready table (Topic 20)."""
    # TODO 0b: paste your Topic 20 build_analysis_table() body here.
    raise NotImplementedError("Complete this function, then delete this line.")


orders = pd.read_csv(DATA_DIR / "orders.csv")
customers = pd.read_csv(DATA_DIR / "customers.csv")
products = pd.read_csv(DATA_DIR / "products.csv")
regions = pd.read_csv(DATA_DIR / "regions.csv")
returns = pd.read_csv(DATA_DIR / "returns.csv")

analysis = build_analysis_table(orders, customers, products, regions, returns)
'''))
    cells.append(code(CHECK2))

    cells.append(md(PART3_MD))
    cells.append(code(PART3_TODO))
    cells.append(code(CHECK3))

    cells.append(md(PART4_MD))
    cells.append(code(PART4_TODO))
    cells.append(code(CHECK4))

    cells.append(md(PART5_MD))
    cells.append(code(PART5_TODO))
    cells.append(code(CHECK5))

    cells.append(md(PART6_MD))
    cells.append(code(PART6_TODO))
    cells.append(code(CHECK6))

    cells.append(md(PART7_MD))
    cells.append(code(PART7_TODO))
    cells.append(code(CHECK7))

    cells.append(md(PART8_MD))
    cells.append(code(PART8_TODO))
    cells.append(code(CHECK8))

    cells.append(md(PART9_MD))
    cells.append(code(PART9_TODO))
    cells.append(code(CHECK9))

    cells.append(md(PART10_MD))
    cells.append(md(RUBRIC_MD))
    cells.append(md(REFERENCES_MD))
    return nb(cells)


def build_solutions():
    cells = [md(ASSIGNMENT_TITLE + " - Instructor Solutions\n" + ASSIGNMENT_SCENARIO)]
    cells.append(md(ASSIGNMENT_SUBMIT))
    cells.append(md(ASSIGNMENT_HOWTO))
    cells.append(md("---"))
    cells.append(code('''
from pathlib import Path
import json

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

PALETTE = {
    "blue": "#2a78d6", "aqua": "#1baf7a", "yellow": "#eda100", "green": "#008300",
    "violet": "#4a3aa7", "red": "#e34948", "magenta": "#e87ba4", "orange": "#eb6834",
}
MUTED = "#c3c2b7"
INK = "#0b0b0b"


def find_data_dir():
    candidates = [Path.cwd() / "data", Path.cwd() / "data_visualization" / "data",
                  Path.cwd().parent.parent / "data_visualization" / "data"]
    for candidate in candidates:
        if (candidate / "orders.csv").exists():
            return candidate
    raise FileNotFoundError("Could not find orders.csv. Looked in: " +
                             ", ".join(str(c) for c in candidates))


DATA_DIR = find_data_dir()
pd.set_option("display.max_columns", 30)
plt.rcParams["figure.dpi"] = 110
print("data folder:", DATA_DIR)
'''))

    cells.append(md(PART1_MD))
    cells.append(md('''
**Chart-selection memo (solution):**

1. Bar, sorted, one colour with emphasis - comparing a measure across a small set of categories.
2. Line, with a rolling average - a trend over 12 consecutive months.
3. Box plot - the question is about spread and shape, not a single number per category.
4. Heatmap, sequential - two categorical dimensions at once; a grid of colour beats a grid of numbers.
5. Composition (bar or pie, justified) - the question is explicitly "what share of the whole."
'''))

    cells.append(md(PART2_MD))
    cells.append(code('''
def clean_region(series):
    return (series.str.strip().str.replace(r"\\s+", " ", regex=True).str.title())


def build_analysis_table(orders, customers, products, regions, returns):
    """Combine the five raw tables into one analysis-ready table (Topic 20)."""
    expected_rows = len(orders)
    customers = customers.copy()
    customers["region"] = clean_region(customers["region"])
    products = products.drop_duplicates(subset="product_id", keep="first")
    customers = customers.merge(regions, on="region", how="left", validate="m:1")
    table = (orders
             .merge(customers, on="customer_id", how="left", validate="m:1")
             .merge(products, on="product_id", how="left", validate="m:1"))
    returned_ids = set(returns["order_id"])
    table["was_returned"] = table["order_id"].isin(returned_ids)
    table["order_date"] = pd.to_datetime(table["order_date"])
    table["month"] = table["order_date"].dt.strftime("%b")
    table["weekday"] = table["order_date"].dt.day_name()
    table["revenue_ghs"] = (table["quantity"] * table["unit_price_ghs"]).round(2)
    table["cost_ghs"] = (table["quantity"] * table["unit_cost_ghs"]).round(2)
    table["profit_ghs"] = (table["revenue_ghs"] - table["cost_ghs"]).round(2)
    if len(table) != expected_rows:
        raise ValueError("Row count changed during wrangling.")
    return table.sort_values("order_date").reset_index(drop=True)


orders = pd.read_csv(DATA_DIR / "orders.csv")
customers = pd.read_csv(DATA_DIR / "customers.csv")
products = pd.read_csv(DATA_DIR / "products.csv")
regions = pd.read_csv(DATA_DIR / "regions.csv")
returns = pd.read_csv(DATA_DIR / "returns.csv")

analysis = build_analysis_table(orders, customers, products, regions, returns)
'''))
    cells.append(code(CHECK2))

    cells.append(md(PART3_MD))
    cells.append(code(PART3_SOLUTION))
    cells.append(code(CHECK3))

    cells.append(md(PART4_MD))
    cells.append(code(PART4_SOLUTION))
    cells.append(code(CHECK4))

    cells.append(md(PART5_MD))
    cells.append(code(PART5_SOLUTION))
    cells.append(code(CHECK5))

    cells.append(md(PART6_MD))
    cells.append(code(PART6_SOLUTION))
    cells.append(code(CHECK6))

    cells.append(md(PART7_MD))
    cells.append(code(PART7_SOLUTION))
    cells.append(code(CHECK7))

    cells.append(md(PART8_MD))
    cells.append(code(PART8_SOLUTION))
    cells.append(code(CHECK8))

    cells.append(md(PART9_MD))
    cells.append(code(PART9_SOLUTION))
    cells.append(code(CHECK9))

    cells.append(md(PART10_MD.replace(
        "*(Write your answer here.)*",
        "*(Model answer - grade for numbers and reasoning, not exact wording.)*", 1)))
    cells.append(md('''
**Model answers:**

1. **Headline:** Retail drove 2023 profit (GHS 33,442.04 of GHS 65,886.38 total), but order volume - not revenue - was the year's real swing factor, peaking at 115 orders in both August and November.
2. **Most questioned chart:** the heatmap (Part 6) - board members often ask "why Thursday," and the honest answer is this dataset does not say; it shows *where* to look, not *why*.
3. **Composition choice:** a bar chart for the three customer tiers - with only a 46.9-point gap between the smallest and largest share, a pie's slice angles would be harder to compare at a glance than three bar heights.
4. **Limitations:** (a) the dashboard is 2023 only - there is no prior year to compare growth against; (b) "busiest" by order count is not the same as "most profitable" - Part 6's heatmap and Part 3's bar chart answer different questions and should not be read as the same ranking.
5. **Next chart:** a line of profit margin (not just profit) by month, to check whether the Nov-Dec revenue spike from Topic 20 came with the same margin as the rest of the year, or at a discount.
'''))
    cells.append(md(RUBRIC_MD))
    cells.append(md(REFERENCES_MD))
    return nb(cells)


if __name__ == "__main__":
    write(build_main(), HERE / "topic21_data_visualization.ipynb")
    write(build_21a(), HERE / "topic21a_anatomy_of_a_chart.ipynb")
    write(build_21b(), HERE / "topic21b_comparing_categories.ipynb")
    write(build_21c(), HERE / "topic21c_change_over_time.ipynb")
    write(build_21d(), HERE / "topic21d_distributions.ipynb")
    write(build_21e(), HERE / "topic21e_relationships.ipynb")
    write(build_21f(), HERE / "topic21f_composition_and_seaborn.ipynb")
    write(build_21g(), HERE / "topic21g_visualization_practice.ipynb")
    write(build_assignment(), HERE / "assignments" / "topic21_assignment_trading_dashboard.ipynb")
    write(build_solutions(), HERE.parent / "instructor_solutions" / "data_visualization" /
          "topic21_assignment_trading_dashboard_solutions.ipynb")
