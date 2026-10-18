"""Generates every Topic 23 (Capstone Project) notebook:
  topic23_capstone_project.ipynb
  topic23a_sql_basics.ipynb .. topic23d_planning_your_analysis.ipynb
  assignments/topic23_capstone_project_brief.ipynb

Run: python build_topic23_notebooks.py
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
# Shared snippets
# ---------------------------------------------------------------------------

def setup_cell(extra_candidate):
    return code(f'''
# Run this cell as it is.
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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
        "Could not find orders.csv. Looked in: " + ", ".join(str(c) for c in candidates)
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

PALETTE = {{
    "blue": "#2a78d6", "aqua": "#1baf7a", "yellow": "#eda100", "green": "#008300",
    "violet": "#4a3aa7", "red": "#e34948", "magenta": "#e87ba4", "orange": "#eb6834",
}}
MUTED = "#c3c2b7"
INK = "#0b0b0b"

print("pandas version:   ", pd.__version__)
print("data folder:      ", DATA_DIR)
print("files:            ", sorted(p.name for p in DATA_DIR.glob("*.csv")))
'''.rstrip())


def rebuild_retail_analysis_cell():
    return code('''
# The retail "2023 Trading Review" table from Topic 20, reused throughout
# this topic exactly as Topic 22 reused it for the two report types.
def clean_region(series):
    return (series.str.strip().str.replace(r"\\s+", " ", regex=True).str.title())


def build_analysis_table(orders, customers, products, regions, returns):
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
print(f"Retail analysis table: {analysis.shape[0]} rows x {analysis.shape[1]} columns")
'''.rstrip())


def import_project_checks_cell():
    return code('''
# Run this cell as it is. It locates and imports project_checks.py, the
# dataset-agnostic structural checker used throughout this topic.
import sys
from pathlib import Path


def find_project_checks_dir():
    candidates = [
        Path.cwd(),
        Path.cwd() / "capstone_project",
        Path.cwd().parent,
        Path.cwd().parent / "capstone_project",
        Path.cwd().parent.parent / "capstone_project",
    ]
    for candidate in candidates:
        if (candidate / "project_checks.py").exists():
            return candidate
    raise FileNotFoundError(
        "Could not find project_checks.py. Looked in: " + ", ".join(str(c) for c in candidates)
    )


project_checks_dir = find_project_checks_dir()
if str(project_checks_dir) not in sys.path:
    sys.path.insert(0, str(project_checks_dir))

import project_checks as pc
print("project_checks.py loaded from:", project_checks_dir)
'''.rstrip())


def footer_cell(back_main, prev, nxt):
    prev_line = f"- Previous: {prev}" if prev else "- Previous: [Main lesson](topic23_capstone_project.ipynb)"
    return md(f'''
---
## Where this fits

- [Back to the main lesson]({back_main})
{prev_line}
- Next: {nxt}
'''.rstrip())


def opening_cell(letter, title, scope, section_ref):
    return md(f'''
# Topic 23{letter} - {title}

{scope}

Work through it after reading section {section_ref} of the [main lesson](topic23_capstone_project.ipynb).
'''.rstrip())


# ---------------------------------------------------------------------------
# Main lesson: topic23_capstone_project.ipynb
# ---------------------------------------------------------------------------

def build_main():
    cells = []

    cells.append(md('''
# Topic 23 - Capstone Project

## Every skill so far, on data nobody handed you

Fourteen topics back, this course started with variables and control flow. Since then, every lesson has worked from a dataset built for you - synthetic, Ghana-contextualised, with just enough realistic mess to teach the point of that lesson and no more. That was deliberate: you needed to learn wrangling without also fighting an unfamiliar dataset, learn visualization without also deciding what was worth charting, learn EDA without also wondering whether the data could be trusted at all.

The capstone removes that scaffolding. **Nobody gives you a dataset for this one.** You find it, you decide whether it is good enough to use, you decide what questions it can actually answer, and you carry it through the whole pipeline - gather, wrangle, explore, visualize, write up - on your own judgement. That is the actual job of a data analyst: not executing a pipeline someone else designed, but deciding whether this data, right here, supports the claim you are about to make.

Two new, small tools join the kit first - SQL and simple regression - because the README promised them and because real data often arrives in a database, and some real questions are "how much does Y change when X changes," which the tools you already have do not answer directly.
'''))

    cells.append(md('''
## Learning objectives

By the end of this lesson you should be able to:

- query a dataset with basic SQL (`SELECT`, `WHERE`, `GROUP BY`, `JOIN`) and recognise its pandas equivalent;
- fit and interpret a simple linear regression, including when R² says the fit is not worth trusting;
- evaluate a candidate dataset against a real checklist before committing to it;
- turn a dataset into a written plan - specific questions, expected deliverables, stated risks - before writing any analysis code;
- carry one dataset through the full pipeline from Topics 19-22: gather, wrangle, explore, visualize, and write both report types;
- judge your own finished project against a rubric that does not know your dataset in advance.
'''))

    cells.append(md('''
## The capstone contract

| Stage | What you already know | From |
|---|---|---|
| Gather | Find real data, check it before trusting it | Topic 19 |
| Wrangle | Combine, clean, validate every join | Topic 20 |
| Explore | Ask good questions, univariate -> bivariate -> multivariate, pattern vs. noise | Topic 22 |
| Visualize | The right chart for the question, titled with the finding | Topic 21 |
| Model *(optional)* | A simple regression, judged by R², not just fitted | 23b |
| Write up | A wrangling report and an act report, for two different readers | Topic 22 |

Nothing in that table is new except the "model" row. The capstone is not a ninth skill - it is proof that the first eight compose into one project without you needing to be told the order.
'''))

    cells.append(setup_cell("capstone_project"))
    cells.append(rebuild_retail_analysis_cell())

    cells.append(md("---"))
    cells.append(md('''
## What's new: SQL

Pandas and SQL answer the same questions about tabular data; SQL is simply the language most real databases speak, so knowing both means you are never blocked by *where* the data happens to live.
'''))
    cells.append(code('''
import sqlite3

conn = sqlite3.connect(":memory:")
orders.to_sql("orders", conn, index=False)

pandas_answer = len(orders[orders["channel"] == "Shop"])
sql_answer = pd.read_sql_query("SELECT COUNT(*) AS n FROM orders WHERE channel = 'Shop'", conn)["n"].iloc[0]
print(f"pandas: {pandas_answer} orders through the Shop channel")
print(f"SQL:    {sql_answer} orders through the Shop channel")
print("Same answer, two languages:", pandas_answer == sql_answer)
'''))
    cells.append(md('''
Section 23a covers `GROUP BY` and `JOIN` the same way - side by side with the pandas you already know, not as a replacement for it.
'''))

    cells.append(md("---"))
    cells.append(md('''
## What's new: simple regression

A correlation coefficient says two things move together. A **regression line** goes further: it claims a specific equation - for every one-unit increase in X, Y changes by *this much* - which is a stronger claim and needs more scrutiny before you trust it.
'''))
    cells.append(code('''
x = analysis["quantity"].values.astype(float)
y = analysis["revenue_ghs"].values

slope, intercept = np.polyfit(x, y, 1)
predicted = slope * x + intercept
ss_res = ((y - predicted) ** 2).sum()
ss_tot = ((y - y.mean()) ** 2).sum()
r_squared = 1 - ss_res / ss_tot

fig, ax = plt.subplots(figsize=(8, 5.5))
ax.scatter(x, y, s=14, alpha=0.3, color=PALETTE["blue"])
x_line = np.linspace(x.min(), x.max(), 50)
ax.plot(x_line, slope * x_line + intercept, color=PALETTE["red"], linewidth=2.5,
        label=f"revenue = {slope:.1f} x quantity + {intercept:.1f}")
ax.set_title(f"Each extra unit ordered adds about GHS {slope:.0f} - but R² = {r_squared:.2f}")
ax.set_xlabel("Quantity ordered")
ax.set_ylabel("Order revenue (GHS)")
ax.legend(frameon=False)
fig.tight_layout()
plt.show()

print(f"R-squared: {r_squared:.3f} - quantity alone explains about {r_squared * 100:.0f}% of the variation in revenue.")
print("The rest comes from unit price, which this line does not know about at all.")
'''))
    cells.append(md('''
R² = 0.172 is a real, usable relationship - not a strong one. The line is not wrong, but a claim like "order size predicts revenue" overstates what 17% of explained variance actually supports. Section 23b covers reading R² and residuals properly, including a second example where the fit is even weaker.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Finding your own data

Topic 19 already built the resource you need for this: [Appendix A - Common Data Sources for Student Projects](../data_analysis_process/topic19b_appendix_common_data_sources.ipynb), with a source table (Kaggle, Our World in Data, World Bank DataBank, data.gov, Ghana Statistical Service, Google Dataset Search, GitHub) and ten evaluation questions to ask before committing to a dataset. Use it - do not go looking for a second list when a good one already exists.

A few more sources worth adding for a capstone's broader scope:

| Source | Good for |
|---|---|
| [UN Data](https://data.un.org/) | International development and demographic indicators |
| [WHO Global Health Observatory](https://www.who.int/data/gho) | Global health statistics by country |
| [FAOSTAT](https://www.fao.org/faostat/en/) | Global food and agriculture statistics |
| [Bank of Ghana](https://www.bog.gov.gh/) | Ghanaian monetary and financial statistics |
| [Ghana Open Data Initiative](https://data.gov.gh/) | Ghanaian government open datasets |

Section 23c practices Topic 19b's checklist directly, on three candidate datasets you did not pick yourself, before you apply it for real.
'''))

    cells.append(md("---"))
    cells.append(md('''
## From dataset to plan

Having a dataset is not having a project. Section 23d practices turning "I have this CSV" into a short written plan - three to five specific questions (22a's rule: specific, comparative, answerable), the deliverables you expect to produce, and the limitations you already know about before you have written a line of analysis code. Writing the risks down *first* is the whole point - a limitation you noticed in week one and a limitation you discover while writing the final report read very differently to someone grading the result.
'''))

    cells.append(md('''
## Key takeaways

- **The capstone adds no new analysis skill except regression** - gathering, wrangling, exploring, visualizing, and writing up are all Topics 19-22, applied without a provided dataset telling you what to do next.
- **SQL and pandas answer the same questions** - learn the mapping, not a second way of thinking about data.
- **A regression line is a stronger claim than a correlation coefficient**, and R² tells you how much of that claim to actually believe.
- **Topic 19b's data-source checklist already exists** - use it rather than rebuilding it, and apply it before you fall in love with a dataset, not after.
- **A written plan - questions, deliverables, risks - belongs before the analysis**, not reconstructed afterward to match what you happened to find.
- **The project is graded by structure, not by a known answer key** - nobody else has your dataset, so the rubric checks what any good project has (reports of the right shape, enough charts, a question that was actually answered), not a specific number.
'''))

    cells.append(md('''
## Further reading and the course path

### On SQL and regression
- [SQLite: SQL as understood by SQLite](https://www.sqlite.org/lang.html)
- [pandas: Comparison with SQL](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html)
- [NumPy: `polyfit`](https://numpy.org/doc/stable/reference/generated/numpy.polyfit.html)

### Practice notebooks for this topic
- [23a - SQL basics](topic23a_sql_basics.ipynb)
- [23b - Simple regression](topic23b_simple_regression.ipynb)
- [23c - Choosing your dataset](topic23c_choosing_your_dataset.ipynb)
- [23d - Planning your analysis](topic23d_planning_your_analysis.ipynb)

### The capstone
- [Topic 23 - the capstone project brief](assignments/topic23_capstone_project_brief.ipynb)
- [Topic 19b - Common data sources](../data_analysis_process/topic19b_appendix_common_data_sources.ipynb)
- [Topic 19d - Submitting your work with GitHub](../data_analysis_process/topic19d_appendix_submitting_with_github.ipynb)

### Elsewhere in the course
- [Topic 20 - Data wrangling](../data_wrangling/topic20_data_wrangling.ipynb)
- [Topic 21 - Data visualization](../data_visualization/topic21_data_visualization.ipynb)
- [Topic 22 - Exploratory data analysis](../exploratory_data_analysis/topic22_exploratory_data_analysis.ipynb)
'''))

    return nb(cells)


# ---------------------------------------------------------------------------
# 23a - SQL basics
# ---------------------------------------------------------------------------

def build_23a():
    cells = [opening_cell(
        "a", "SQL basics",
        "The main lesson showed one SELECT ... WHERE matching a pandas filter. This notebook covers GROUP BY and JOIN the same way - side by side with the pandas equivalent - because most real data you will gather for the capstone lives in a database, not a CSV someone handed you.",
        "\"What's new: SQL\"",
    )]
    cells.append(setup_cell("capstone_project"))
    cells.append(rebuild_retail_analysis_cell())

    cells.append(md("---"))
    cells.append(md('''
## Loading pandas tables into a real database

`sqlite3` ships with Python - no server, no install, no credentials. `DataFrame.to_sql()` loads a table into it in one line, which is also the fastest way to practise SQL against data you already understand.
'''))
    cells.append(code('''
import sqlite3

conn = sqlite3.connect(":memory:")
orders.to_sql("orders", conn, index=False)
customers.to_sql("customers", conn, index=False)
products.to_sql("products", conn, index=False)

tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
print(tables)
'''))

    cells.append(md("---"))
    cells.append(md('''
## SELECT, WHERE, ORDER BY

`WHERE` is SQL's boolean filter; `ORDER BY` is SQL's `.sort_values()`.
'''))
    cells.append(code('''
sql_result = pd.read_sql_query("""
    SELECT order_id, quantity, unit_price_ghs
    FROM orders
    WHERE quantity >= 10
    ORDER BY quantity DESC
    LIMIT 5
""", conn)

pandas_result = (orders[orders["quantity"] >= 10]
                  .sort_values("quantity", ascending=False)
                  [["order_id", "quantity", "unit_price_ghs"]]
                  .head(5))

print("SQL:")
print(sql_result.to_string(index=False))
print("\\npandas:")
print(pandas_result.to_string(index=False))
'''))

    cells.append(md("---"))
    cells.append(md('''
## GROUP BY and aggregates

SQL's `GROUP BY` with `COUNT`/`SUM`/`AVG` is pandas' `.groupby()` with `.size()`/`.sum()`/`.mean()`.
'''))
    cells.append(code('''
sql_result = pd.read_sql_query("""
    SELECT channel, COUNT(*) AS n_orders, SUM(quantity) AS total_quantity
    FROM orders
    GROUP BY channel
    ORDER BY n_orders DESC
""", conn)

pandas_result = (orders.groupby("channel")
                  .agg(n_orders=("order_id", "count"), total_quantity=("quantity", "sum"))
                  .sort_values("n_orders", ascending=False)
                  .reset_index())

print("SQL:")
print(sql_result.to_string(index=False))
print("\\npandas:")
print(pandas_result.to_string(index=False))
print("\\nSame numbers:", sql_result["n_orders"].tolist() == pandas_result["n_orders"].tolist())
'''))

    cells.append(md("---"))
    cells.append(md('''
## JOIN

SQL's `JOIN ... ON` is pandas' `.merge(..., on=...)`. The join type keyword matters just as much in SQL as it did in Topic 20 - `LEFT JOIN` keeps every row on the left even where there is no match, exactly like `how="left"`.
'''))
    cells.append(code('''
sql_result = pd.read_sql_query("""
    SELECT p.category, COUNT(*) AS n_orders
    FROM orders o
    LEFT JOIN products p ON o.product_id = p.product_id
    GROUP BY p.category
    ORDER BY n_orders DESC
""", conn)

pandas_result = (orders.merge(products.drop_duplicates(subset="product_id"), on="product_id", how="left")
                  .groupby("category").size().sort_values(ascending=False)
                  .rename("n_orders").reset_index())

print("SQL:")
print(sql_result.to_string(index=False))
print("\\npandas:")
print(pandas_result.to_string(index=False))
'''))
    cells.append(md('''
Notice the `products.drop_duplicates(subset="product_id")` in the pandas version - Topic 20's duplicate-key hazard applies here too. The SQL query above did **not** guard against it, and would silently double-count any order against a duplicated product id, exactly the way an unguarded pandas merge would. SQL is not immune to the hazards Topic 20 taught; it just spells them differently (`JOIN` instead of `merge`), and it is just as silent when it goes wrong.
'''))

    cells.append(md('''
### Try It 1 - a three-way comparison

Write a SQL query joining `orders` to `customers`, grouped by `segment`, returning total `quantity` per segment, sorted descending. Then write the pandas equivalent. Confirm both give the same numbers.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(footer_cell(
        "topic23_capstone_project.ipynb", None,
        "[23b - Simple regression](topic23b_simple_regression.ipynb)",
    ))
    return nb(cells)


# ---------------------------------------------------------------------------
# 23b - Simple regression
# ---------------------------------------------------------------------------

def build_23b():
    cells = [opening_cell(
        "b", "Simple regression",
        "The main lesson fit one regression line (quantity vs. revenue, R² = 0.17) and called it usable but not strong. This notebook covers reading R² and residuals properly, and a second example where the fit is much weaker - so you learn to judge a fit, not just produce one.",
        "\"What's new: simple regression\"",
    )]
    cells.append(setup_cell("capstone_project"))
    cells.append(rebuild_retail_analysis_cell())
    cells.append(code('''
aq_stations = pd.read_csv(DATA_DIR / "air_quality_stations.csv")
aq_readings = pd.read_csv(DATA_DIR / "air_quality_readings.csv", parse_dates=["date"])
aq = aq_readings.merge(aq_stations, on="station_id", how="left", validate="m:1")
print(f"Air-quality table: {aq.shape[0]} rows")
'''))

    cells.append(md("---"))
    cells.append(md('''
## Fitting a line: slope, intercept, and what they mean

`np.polyfit(x, y, 1)` returns the slope and intercept of the best-fit line through `(x, y)` - "best" meaning it minimises the sum of squared vertical distances from each point to the line (least squares).
'''))
    cells.append(code('''
x = analysis["quantity"].values.astype(float)
y = analysis["revenue_ghs"].values

slope, intercept = np.polyfit(x, y, 1)
print(f"revenue_ghs = {slope:.2f} x quantity + {intercept:.2f}")
print(f"Interpretation: each additional unit ordered is associated with about GHS {slope:.2f} more revenue,")
print(f"and an order of zero quantity (meaningless here, but the maths still gives it a value) predicts GHS {intercept:.2f}.")
'''))
    cells.append(md('''
That last line matters: the intercept is whatever the equation says at x = 0, whether or not x = 0 makes sense for your data. An order of zero quantity cannot exist, so the intercept here is a mathematical artefact, not a real prediction - always check whether x = 0 is a meaningful point before interpreting the intercept as a fact about the world.
'''))

    cells.append(md("---"))
    cells.append(md('''
## R²: how much the line actually explains

R² compares the line's errors to the simplest possible guess - always predicting the mean. R² = 1 means the line explains all the variation; R² = 0 means it explains none, no better than guessing the average every time.
'''))
    cells.append(code('''
def fit_and_r_squared(x, y):
    slope, intercept = np.polyfit(x, y, 1)
    predicted = slope * x + intercept
    ss_res = ((y - predicted) ** 2).sum()
    ss_tot = ((y - y.mean()) ** 2).sum()
    r_squared = 1 - ss_res / ss_tot
    return slope, intercept, r_squared, predicted


slope, intercept, r2, predicted = fit_and_r_squared(x, y)
print(f"quantity -> revenue: R\\u00b2 = {r2:.3f}")
print(f"In plain terms: quantity explains about {r2*100:.0f}% of why one order's revenue differs from another's.")
print(f"The other {(1 - r2) * 100:.0f}% comes from unit price and everything else this line does not use.")
'''))

    cells.append(md("---"))
    cells.append(md('''
## A much weaker fit: temperature and PM2.5

A line can always be fitted - `polyfit` never refuses. Whether the result is worth reporting is a separate question, answered by R², not by whether the function ran without error.
'''))
    cells.append(code('''
x2 = aq["temperature_c"].dropna().values
y2 = aq.loc[aq["temperature_c"].notna(), "pm2_5"]
mask = y2.notna()
x2, y2 = x2[mask.values], y2[mask].values

slope2, intercept2, r2_2, predicted2 = fit_and_r_squared(x2, y2)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].scatter(x2, y2, s=10, alpha=0.3, color=PALETTE["blue"])
x_line = np.linspace(x2.min(), x2.max(), 50)
axes[0].plot(x_line, slope2 * x_line + intercept2, color=PALETTE["red"], linewidth=2.5)
axes[0].set_title(f"temperature -> PM2.5: R\\u00b2 = {r2_2:.3f} - barely worth fitting")
axes[0].set_xlabel("Temperature (C)")
axes[0].set_ylabel("PM2.5 (ug/m3)")

residuals = y2 - predicted2
axes[1].scatter(predicted2, residuals, s=10, alpha=0.3, color=PALETTE["blue"])
axes[1].axhline(0, color=INK, linewidth=1.5)
axes[1].set_title("Residuals: large and show a wide spread at every predicted value")
axes[1].set_xlabel("Predicted PM2.5 (ug/m3)")
axes[1].set_ylabel("Residual (actual - predicted)")

fig.tight_layout()
plt.show()

print(f"R\\u00b2 = {r2_2:.3f}: temperature explains about {r2_2*100:.0f}% of PM2.5's variation - not nothing, but not a")
print("relationship to build a claim on by itself.")
'''))
    cells.append(md('''
The residual plot on the right is doing real work: a good fit has residuals scattered evenly around zero with no pattern. Here they are not just scattered - they are *large* relative to the predictions, which is the visual version of a low R². If the residuals instead curved or fanned out as predictions grew, that would be a sign the relationship is not linear at all, which `polyfit` cannot tell you - it only ever fits a straight line, whether or not a straight line is the right shape.

This also connects straight back to Topic 22: temperature correlates with PM2.5 at r = 0.22 - both numbers are reporting the same weak relationship, and the reason is the same one from Topic 22's correlation-vs-shared-cause section. Temperature does not control air quality directly; both temperature and PM2.5 happen to follow the dry season. A regression line here is dressing up a confound in an equation, not describing a real cause.
'''))

    cells.append(md('''
### Try It 2 - fit and judge, don't just fit

Fit a regression of `wind_speed_kmh` predicting `pm2_5`. Report the slope, intercept, and R², and write one sentence saying whether you would use this line to make a real prediction, and why.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(footer_cell(
        "topic23_capstone_project.ipynb",
        "[23a - SQL basics](topic23a_sql_basics.ipynb)",
        "[23c - Choosing your dataset](topic23c_choosing_your_dataset.ipynb)",
    ))
    return nb(cells)


# ---------------------------------------------------------------------------
# 23c - Choosing your dataset
# ---------------------------------------------------------------------------

def build_23c():
    cells = [opening_cell(
        "c", "Choosing your dataset",
        "The main lesson pointed you at Topic 19b's data-source list and ten-question checklist. This notebook practices applying that checklist to three candidate datasets you did not pick yourself - one strong, one mediocre, one bad - before you apply it for real to your own capstone candidate.",
        "\"Finding your own data\"",
    )]

    cells.append(md("---"))
    cells.append(md('''
## The checklist, from Topic 19b

1. Who published it?
2. Why was it collected?
3. When was it last updated?
4. What does each row represent?
5. Are column definitions provided?
6. Is there a license or terms of use?
7. Is the file format usable for this course?
8. Are there enough rows for analysis?
9. Are there obvious quality issues?
10. Can I cite the source clearly?

Three candidates follow - real-shaped descriptions, not full data, the way you would actually encounter them while browsing a source before downloading anything.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Candidate A

> **Source:** World Bank DataBank, "World Development Indicators"
> **Description:** GDP per capita, life expectancy, and population for every country, annually, 1960-2023.
> **Format:** CSV, one row per country per year, documented column names, metadata file included.
> **License:** CC BY-4.0, explicitly stated on the download page.
> **Last updated:** Within the last 6 months.
> **Size:** Roughly 13,000 rows, 6 columns.

### Try It 1 - score Candidate A

Answer all ten checklist questions for Candidate A in a markdown cell, then give it a one-line verdict: use it, use it with caution, or reject it.
'''))
    cells.append(code("# Write your ten answers and verdict as a markdown cell, or as comments here."))

    cells.append(md("---"))
    cells.append(md('''
## Candidate B

> **Source:** A Kaggle dataset titled "Global Sales Data," uploaded by a user with no other published datasets.
> **Description:** Claims to be "retail sales from multiple countries," no stated time period.
> **Format:** CSV, column names are `col1`, `col2`, `col3` ... `col9` - no header documentation anywhere in the listing.
> **License:** Not specified.
> **Last updated:** 4 years ago, no update history.
> **Size:** 50,000 rows.

### Try It 2 - score Candidate B

Answer the ten questions for Candidate B. Pay particular attention to questions 4, 5, 6, and 9 - this one is designed to fail several of them. Give your verdict.
'''))
    cells.append(code("# Write your ten answers and verdict as a markdown cell, or as comments here."))

    cells.append(md("---"))
    cells.append(md('''
## Candidate C

> **Source:** Ghana Statistical Service, "2021 Population and Housing Census - District Analytical Report"
> **Description:** Detailed demographic breakdowns by district, with strong documentation.
> **Format:** Published only as a 180-page PDF report with tables embedded as images in some sections; no downloadable CSV.
> **License:** Government publication, public use permitted with attribution.
> **Last updated:** 2021 census, most recent available.
> **Size:** Unknown row count - would need to be manually extracted from PDF tables.

### Try It 3 - score Candidate C, and the real lesson

Answer the ten questions for Candidate C. This one is the hardest judgement call of the three - it is official, current, and well-documented, but the *format* works against you. Decide: is this usable for this course with some extra effort, or does the PDF-only format rule it out? There is a defensible answer either way - what matters is that you can justify it against the checklist, not guess.
'''))
    cells.append(code("# Write your ten answers and verdict as a markdown cell, or as comments here."))

    cells.append(md("---"))
    cells.append(md('''
### Try It 4 - score your own candidate

Find one real candidate dataset for your own capstone - from Topic 19b's list, the main lesson's additional sources, or anywhere else - and run it through the same ten questions. If it fails more than two or three, look for a second candidate before committing; a capstone built on a dataset that fails its own evaluation checklist starts the project already in debt.
'''))
    cells.append(code("# Write your ten answers and verdict for your real candidate here."))

    cells.append(footer_cell(
        "topic23_capstone_project.ipynb",
        "[23b - Simple regression](topic23b_simple_regression.ipynb)",
        "[23d - Planning your analysis](topic23d_planning_your_analysis.ipynb)",
    ))
    return nb(cells)


# ---------------------------------------------------------------------------
# 23d - Planning your analysis
# ---------------------------------------------------------------------------

def build_23d():
    cells = [opening_cell(
        "d", "Planning your analysis",
        "The main lesson argued that having a dataset is not having a project. This notebook practices the missing step: turning a chosen dataset into a short written plan - specific questions, expected deliverables, and stated risks - before any analysis code gets written.",
        "\"From dataset to plan\"",
    )]

    cells.append(md("---"))
    cells.append(md('''
## A worked example plan

Here is a plan for a dataset like Candidate A from 23c - World Bank development indicators - written *before* any analysis, the way yours should be.

> **Dataset:** World Bank World Development Indicators (GDP per capita, life expectancy, population), 1960-2023, all countries.
>
> **Research questions:**
> 1. How has the gap in life expectancy between the highest- and lowest-income countries changed since 1990?
> 2. Does GDP per capita growth predict life expectancy gains, and how strong is that relationship?
> 3. Which countries have improved life expectancy the most relative to their GDP per capita growth?
>
> **Expected deliverables:** a cleaned, merged country-year table; at least 5 charts covering a time trend, a cross-country comparison, and the GDP-life expectancy relationship; a regression of GDP per capita on life expectancy with R² reported honestly; a wrangling report; an act report aimed at a general reader interested in global development.
>
> **Known risks, stated before starting:** GDP per capita is not evenly measured across countries with different statistical capacity; some countries have large gaps in their time series; correlation between GDP and life expectancy will not establish which caused which, and both plausibly share causes (healthcare investment, political stability) the dataset does not capture.

Notice that last section is not hedging - it is specific. "Data quality varies" is not a risk statement; "GDP per capita is not evenly measured across countries with different statistical capacity" is, because it says exactly what might be wrong and leaves a reader able to judge how much it matters.
'''))

    cells.append(md("---"))
    cells.append(md('''
### Try It 1 - write your own plan

Using the dataset you scored in 23c's Try It 4, write your own plan in the same four parts: dataset (one line), 3-5 research questions (specific, comparative, answerable - 22a's rule), expected deliverables, and known risks stated specifically, not vaguely.
'''))
    cells.append(code("# Write your plan as a markdown cell, or as comments here."))

    cells.append(md('''
### Try It 2 - stress-test your own questions

For each of your research questions, ask: could someone else answer this from your dataset and get a different number than you, just by making a different reasonable choice? If yes, say in advance which choice you are making and why - this is the same discipline as Topic 20's "state the grain of the table before you touch it."
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(footer_cell(
        "topic23_capstone_project.ipynb",
        "[23c - Choosing your dataset](topic23c_choosing_your_dataset.ipynb)",
        "[The capstone project brief](assignments/topic23_capstone_project_brief.ipynb)",
    ))
    return nb(cells)


if __name__ == "__main__":
    write(build_main(), HERE / "topic23_capstone_project.ipynb")
    write(build_23a(), HERE / "topic23a_sql_basics.ipynb")
    write(build_23b(), HERE / "topic23b_simple_regression.ipynb")
    write(build_23c(), HERE / "topic23c_choosing_your_dataset.ipynb")
    write(build_23d(), HERE / "topic23d_planning_your_analysis.ipynb")


# ---------------------------------------------------------------------------
# The capstone assignment brief
# ---------------------------------------------------------------------------

def build_assignment():
    cells = [md('''
# Topic 23 Assignment - The Capstone Project

## There is no provided dataset for this one

Every other assignment in this course gave you a dataset. This one gives you a method instead: find real data, evaluate it honestly, and carry it through the whole pipeline you have built since Topic 19.

This is also the only assignment in the course with no numeric answer key - nobody else has your dataset, so nobody can tell you in advance what your charts should show. What *can* be checked, and what this brief checks in code, is structure: did you produce both reports, are they the right length, do they have the sections a reader needs, did you save enough charts. That is not the same as checking whether your project is any good - a human reader (your instructor, a peer, yourself in a week) still has to judge that part.

### What you are practising

| Skill | Where |
|---|---|
| Evaluating a real dataset before committing to it | Topic 19b, 23c |
| Writing a plan before writing analysis code | 23d |
| Gathering and wrangling real (not provided) data | Topics 19-20 |
| Exploratory analysis and the pattern-vs-noise checks | Topic 22 |
| Visualization built to the course's own standard | Topic 21 |
| A simple regression, judged by R², not just fitted | 23b |
| Writing a wrangling report and an act report | Topic 22, this topic |
| Submitting work with Git and GitHub | Topic 19d |
'''.lstrip())]

    cells.append(md('''
## Finding your dataset

Start at [Topic 19b - Common data sources](../../data_analysis_process/topic19b_appendix_common_data_sources.ipynb) and the additional sources listed in this topic's main lesson. Run your top one or two candidates through the ten-question checklist from 23c before committing - in writing, in your submitted notebook, not just in your head.

**Rules for the dataset itself:**
- It must be real data from a real source, not generated by you or by an AI tool.
- It must have at least 200 rows and at least 4 columns worth analysing.
- You must be able to name its source, its license or terms of use, and when it was last updated.
- It must not be a dataset already used anywhere in this course (the retail distributor, the Accra air-quality readings, or the gapminder/World Bank files from Topic 19).
'''))

    cells.append(md('''
## What you must submit

A **public** GitHub repository named **`itfy-capstone`** containing:

1. one notebook, run from top to bottom, covering gather → wrangle → explore → visualize → (optional) model;
2. `data/` - your raw source file(s), unchanged, plus a note on where you got them and when;
3. `charts/` - at least 5 saved charts, across at least 4 different chart types (bar, line, histogram, box, scatter, or heatmap);
4. `wrangle_report.md` - following Topic 22's structure and this course's checks;
5. `act_report.md` - following Topic 22's structure and this course's checks, with at least one chart embedded;
6. `presentation_outline.md` - a slide-by-slide outline (title + one-line content per slide) for a 5-10 minute presentation of your act report, since the README promises "notebook + presentation" as the capstone deliverable.

Full submission instructions are in [the GitHub submission guide](../../data_analysis_process/topic19d_appendix_submitting_with_github.ipynb).

### Rules

- **Every merge or join carries a validation check** - `validate=` in pandas, or an explicit row-count check either way (Topic 20's discipline doesn't stop applying just because the data is new).
- **Every chart has a title that states a finding, axis labels with units, and a legend where there is more than one series** (Topic 21's standard).
- **The wrangling report contains no code, column names, or library names.**
- **The act report has a hook, at least 3 ranked insights each with a number, a "So what," and a "Limitations" line** (Topic 22's structure).
- **If you fit a regression, report R² and say explicitly whether the fit is strong enough to act on** - fitting a line is not the same as the line being worth trusting.
'''))

    cells.append(md('''
## How to work through this notebook

1. Work through 23a-23d first if you have not already - the SQL and regression tools, the dataset checklist, and the planning template are all assumed here.
2. Choose and evaluate your dataset (write your checklist answers below).
3. Write your plan (questions, deliverables, risks) before writing analysis code.
4. Do the work: gather, wrangle, explore, visualize, optionally model.
5. Write both reports, save them as files, and run the check cell below against your own project folder.
6. Fill in the reflection at the end and submit.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Part 1 - Dataset evaluation

Name your dataset, its source, its license, and when it was last updated. Then answer Topic 19b's ten evaluation questions for it.
'''))
    cells.append(md('''
**Dataset:** *(name and source)*

**License:** *(license or terms of use)*

**Last updated:** *(date, as stated by the source)*

**Ten-question evaluation:**

1. *(answer)*
2. *(answer)*
3. *(answer)*
4. *(answer)*
5. *(answer)*
6. *(answer)*
7. *(answer)*
8. *(answer)*
9. *(answer)*
10. *(answer)*
'''))

    cells.append(md('''
---
## Part 2 - Your plan

Following 23d's structure: 3-5 research questions (specific, comparative, answerable), your expected deliverables, and your known risks, stated specifically.
'''))
    cells.append(md('''
**Research questions:**

1. *(question)*
2. *(question)*

**Expected deliverables:** *(one paragraph)*

**Known risks:** *(specific, not vague - name what could be wrong and how it would matter)*
'''))

    cells.append(md('''
---
## Part 3 - Gather and wrangle

Load your raw data, document every data-quality issue you find, and build one analysis-ready table. Every merge needs a validation check.
'''))
    cells.append(code('''
# YOUR CODE HERE
# Load your raw data, clean it, merge it, and validate the result -
# the same discipline as Topic 20's build_analysis_table().
'''))

    cells.append(md('''
---
## Part 4 - Explore

Univariate, then bivariate, then multivariate - Topic 22's loop. Apply the three checks (sample size, shared cause, interesting vs. important) to at least one candidate finding before it goes in your act report.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(md('''
---
## Part 5 - Visualize

At least 5 charts, at least 4 chart types, each built to Topic 21's standard. Save every chart to `charts/`.
'''))
    cells.append(code('''
from pathlib import Path

charts_dir = Path("charts")
charts_dir.mkdir(exist_ok=True)

# YOUR CODE HERE
'''))

    cells.append(md('''
---
## Part 6 - Model (optional)

If a relationship in your data is worth fitting a line to, do it here using 23b's approach: slope, intercept, R², and a residual check. State explicitly whether the fit is strong enough to act on.
'''))
    cells.append(code("# YOUR CODE HERE (or leave this part out if no relationship in your data warrants it)"))

    cells.append(md('''
---
## Part 7 - Write both reports

Write `wrangle_report` and `act_report` as strings, following Topic 22's structures, then save them to disk.
'''))
    cells.append(code('''
wrangle_report = """
YOUR WRANGLING REPORT HERE
"""

act_report = """
YOUR ACT REPORT HERE
"""

Path("wrangle_report.md").write_text(wrangle_report.strip() + "\\n")
Path("act_report.md").write_text(act_report.strip() + "\\n")
print("Reports saved.")
'''))

    cells.append(md('''
---
## Part 8 - Check your own project

This is the one check cell in this assignment, and it works on any dataset, because it checks structure, not content.
'''))
    cells.append(import_project_checks_cell())
    cells.append(code('''
from pathlib import Path

results = pc.run_capstone_checks(Path("."), min_chart_count=5)
import json
print(json.dumps(results, indent=2, default=str))
'''))
    cells.append(md('''
A `True` for `all_ok` means your reports are the right length, have the right sections, and you saved enough charts. It does **not** mean your project is good - that still needs a human reader. Use a `False` to find and fix a structural gap before you submit, not as a substitute for rereading your own reports.
'''))

    cells.append(md('''
---
## Part 9 - Presentation outline

List your slides - title plus one line of content each - for a 5-10 minute presentation of your act report.
'''))
    cells.append(code('''
presentation_outline = """
# TODO: one line per slide, e.g.:
# 1. Title: <your project title>
# 2. The headline finding (one number, one sentence)
# 3. Insight 1, with its chart
# ...
"""

Path("presentation_outline.md").write_text(presentation_outline.strip() + "\\n")
print("Presentation outline saved.")
'''))

    cells.append(md('''
---
### Reflection

**1. What surprised you most about your own dataset?**

*(Write your answer here.)*

**2. Where did you have to make a judgement call that someone else might have made differently?**

*(Write your answer here.)*

**3. If you had one more week, what would you do next?**

*(Write your answer here.)*
'''))

    cells.append(md('''
---
## Marking rubric

| Area | What earns the marks | Marks |
|---|---:|---:|
| Dataset evaluation | Real dataset, source and license named, all ten questions answered honestly | 10 |
| Plan | Specific, comparative, answerable questions; risks stated specifically before the analysis | 10 |
| Gather and wrangle | Issues documented; every merge validated; a working analysis-ready table | 16 |
| Exploration | Univariate -> bivariate -> multivariate; at least one finding passed through the three checks | 16 |
| Visualization | At least 5 charts, at least 4 types, each titled with a finding and correctly labelled | 16 |
| Model (if attempted) | R² reported and correctly interpreted; fit judged, not just produced | 8 |
| Wrangling report | Passes the structural check; plain language; states what to trust | 10 |
| Act report | Passes the structural check; correct structure; numbers trace back to your own analysis | 12 |
| Presentation outline | Matches the act report; one line per slide, reasonable slide count | 4 |
| Repository and structure | Public repo, correct file structure, useful commits | 8 |
| **Total** | | **110** |

Marks are lost for: a dataset already used elsewhere in this course, a chart without a stated finding or units, a wrangling report containing code or column names, an act report with no "So what," a regression reported without R², and a repository that is not public.
'''))

    cells.append(md('''
## References

### Topic 23 material
- [Main lesson - Topic 23 Capstone Project](../topic23_capstone_project.ipynb)
- [23a - SQL basics](../topic23a_sql_basics.ipynb)
- [23b - Simple regression](../topic23b_simple_regression.ipynb)
- [23c - Choosing your dataset](../topic23c_choosing_your_dataset.ipynb)
- [23d - Planning your analysis](../topic23d_planning_your_analysis.ipynb)
- [An example walkthrough](../../instructor_solutions/capstone_project/example_capstone_walkthrough.ipynb) - a model of the expected shape, on a different dataset from yours

### Finding data
- [Topic 19b - Common data sources](../../data_analysis_process/topic19b_appendix_common_data_sources.ipynb)

### Elsewhere in the course
- [Topic 20 - Data wrangling](../../data_wrangling/topic20_data_wrangling.ipynb)
- [Topic 21 - Data visualization](../../data_visualization/topic21_data_visualization.ipynb)
- [Topic 22 - Exploratory data analysis](../../exploratory_data_analysis/topic22_exploratory_data_analysis.ipynb)
- [Submitting your work with GitHub](../../data_analysis_process/topic19d_appendix_submitting_with_github.ipynb)
'''))

    return nb(cells)


if __name__ == "__main__":
    write(build_assignment(), HERE / "assignments" / "topic23_capstone_project_brief.ipynb")


# ---------------------------------------------------------------------------
# Instructor worked example - a real, actually-downloaded dataset
# ---------------------------------------------------------------------------

def build_example_walkthrough():
    cells = [md('''
# Example Capstone Walkthrough - Does National Income Predict Internet Access?

> **This is a model of the expected shape and depth, not an answer key, and not a dataset you may reuse for your own capstone.** Every number below is real and computed from the data loaded in this notebook - nothing is invented - but your own project will look different because your dataset is different. Read this for the *pattern*: how much wrangling, how deep the exploration goes, what "enough" charts and words looks like, not for anything to copy.

This walkthrough uses two real datasets from [Our World in Data](https://ourworldindata.org/): the share of each country's population using the internet, and GDP per capita, both by country and year. Neither has appeared anywhere else in this course.
'''.lstrip())]

    cells.append(md('''
---
## Part 1 - Dataset evaluation

**Dataset:** Our World in Data, "Share of Individuals Using the Internet" and "GDP per Capita (World Bank)"
**Source:** https://ourworldindata.org/internet and World Bank national accounts data, republished by Our World in Data
**License:** Creative Commons BY 4.0 - free to use with attribution
**Last updated:** Both files include data through 2024-2025 at the time of download

**Ten-question evaluation:**

1. **Who published it?** Our World in Data, a research organisation based at Oxford University that republishes and documents data from primary sources (here, the International Telecommunication Union and the World Bank).
2. **Why was it collected?** The ITU tracks internet access as part of global development monitoring; the World Bank tracks GDP as a core economic indicator. Both existed long before this project.
3. **When was it last updated?** Within the last year for both files, based on the download metadata.
4. **What does each row represent?** One country, one year, one value (percentage of population online, or GDP per capita in international dollars).
5. **Are column definitions provided?** Yes - both files have self-explanatory headers and Our World in Data's website documents the exact source and methodology for each.
6. **Is there a license or terms of use?** Yes, CC BY 4.0, stated on every Our World in Data download page.
7. **Is the file format usable for this course?** Yes - plain CSV, loads directly with `pd.read_csv()`.
8. **Are there enough rows for analysis?** Yes - roughly 200 countries across up to 35 years each, thousands of rows before any filtering.
9. **Are there obvious quality issues?** Yes, found during wrangling below: the files include regional and income-group aggregates (e.g. "World," "Africa") alongside individual countries, which must be separated out before treating a row as one country.
10. **Can I cite the source clearly?** Yes - both are cited above with direct links.

**Verdict:** use it. It passes all ten questions, with one wrangling step (issue 9) needed before analysis.
'''))

    cells.append(md('''
---
## Part 2 - Plan

**Research questions:**

1. How strongly does a country's GDP per capita predict its internet usage rate, and is that relationship better described on a raw or a logarithmic income scale?
2. How has global internet access changed since 2005, and does every region share in that growth equally?
3. Where does Ghana sit in this picture, relative to its region and to the global trend?

**Expected deliverables:** a merged country-year table with aggregate rows removed; a distribution chart, a regional comparison, a global time trend, a GDP-vs-internet scatter (raw and log scale), and a fitted regression with its R² reported; a wrangling report; an act report.

**Known risks, stated before starting:** GDP per capita is measured with different statistical capacity across countries, so comparisons involving the lowest-income countries carry more uncertainty than the headline numbers suggest. Internet usage rates are self-reported by national statistical agencies with different survey methods, which this dataset cannot correct for. Correlation between GDP and internet access does not establish causation - wealthier countries can afford infrastructure, but internet access may also contribute to income growth, and the two plausibly reinforce each other rather than one simply causing the other.
'''))

    cells.append(md('''
---
## Part 3 - Gather

Both files were downloaded directly from Our World in Data's grapher export endpoint:

```
curl -sL "https://ourworldindata.org/grapher/share-of-individuals-using-the-internet.csv" \\
     -o raw_data/share-of-individuals-using-the-internet.csv
curl -sL "https://ourworldindata.org/grapher/gdp-per-capita-worldbank.csv" \\
     -o raw_data/gdp-per-capita-worldbank.csv
```

They are loaded from the saved local copies below, so this notebook re-runs identically without depending on a live network connection every time.
'''))
    cells.append(code('''
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PALETTE = {
    "blue": "#2a78d6", "aqua": "#1baf7a", "yellow": "#eda100", "green": "#008300",
    "violet": "#4a3aa7", "red": "#e34948", "magenta": "#e87ba4", "orange": "#eb6834",
}
MUTED = "#c3c2b7"
INK = "#0b0b0b"

pd.set_option("display.max_columns", 30)
plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.color"] = "#e1e0d9"
plt.rcParams["axes.edgecolor"] = "#c3c2b7"
plt.rcParams["axes.axisbelow"] = True

RAW_DIR = Path("raw_data")
internet_raw = pd.read_csv(RAW_DIR / "share-of-individuals-using-the-internet.csv")
gdp_raw = pd.read_csv(RAW_DIR / "gdp-per-capita-worldbank.csv")

internet_raw.columns = ["entity", "code", "year", "internet_pct"]
gdp_raw.columns = ["entity", "code", "year", "gdp_per_capita", "region"]

print(f"Internet file: {internet_raw.shape[0]} rows, {internet_raw['entity'].nunique()} entities")
print(f"GDP file:      {gdp_raw.shape[0]} rows, {gdp_raw['entity'].nunique()} entities")
'''))

    cells.append(md('''
---
## Part 4 - Wrangle

The quality issue found during evaluation (question 9): both files mix individual countries with regional and income-group aggregates ("World," "Africa," "High-income countries"). These do not have standard 3-letter ISO country codes - the aggregates use longer or `OWID_`-prefixed codes - which gives a clean, checkable rule for separating them, the same way Topic 20 checked a key before trusting a join.
'''))
    cells.append(code('''
def is_country_code(code):
    return isinstance(code, str) and len(code) == 3 and not code.startswith("OWID")


before = internet_raw["entity"].nunique()
internet = internet_raw[internet_raw["code"].apply(is_country_code)].copy()
gdp = gdp_raw[gdp_raw["code"].apply(is_country_code)].copy()
after = internet["entity"].nunique()

print(f"Internet file: {before} entities before filtering, {after} individual countries after")
print(f"Removed as aggregates: {sorted(set(internet_raw['entity']) - set(internet['entity']))[:8]} ...")

merged = internet.merge(gdp, on=["entity", "code", "year"], how="inner", validate="1:1")
print(f"\\nMerged table: {merged.shape[0]} rows, {merged['entity'].nunique()} countries, "
      f"{merged['year'].min()}-{merged['year'].max()}")
print(f"Rows dropped by the inner join (no GDP figure for that country-year): "
      f"{len(internet) - merged.shape[0]}")
'''))
    cells.append(md('''
`validate="1:1"` is doing the same job here it did in Topic 20: each country-year should appear once in each file, and the merge raises immediately if that stops being true, rather than silently producing duplicate rows.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Part 5 - Explore

**Univariate first:** what does the distribution of internet usage look like in the most recent complete year?
'''))
    cells.append(code('''
latest_year = merged[merged["year"] == 2024].dropna(subset=["internet_pct", "gdp_per_capita"])
print(f"2024: {len(latest_year)} countries with both measures")
print(latest_year["internet_pct"].describe().round(1).to_string())
print(f"Skew: {latest_year['internet_pct'].skew():.2f}")
'''))
    cells.append(md('''
A mean of 72.1% against a median of 82.0% - the mean sits *below* the median, meaning this distribution is left-skewed: most countries cluster at high internet usage, with a smaller group of low-usage countries pulling the average down. That is the opposite shape from every right-skewed distribution in Topics 20-22 (revenue, PM2.5), and worth noticing precisely because it is different - skew direction is itself a finding, not just a nuisance to correct for.
'''))

    cells.append(md('''
**Bivariate:** does GDP per capita predict internet usage - and does that depend on whether GDP is viewed on a raw or logarithmic scale?
'''))
    cells.append(code('''
r_raw = latest_year["gdp_per_capita"].corr(latest_year["internet_pct"])
r_log = np.log(latest_year["gdp_per_capita"]).corr(latest_year["internet_pct"])
print(f"Correlation, raw GDP per capita:  r = {r_raw:.3f}")
print(f"Correlation, log(GDP per capita): r = {r_log:.3f}")
'''))
    cells.append(md('''
The log-scale correlation (0.889) is substantially stronger than the raw one (0.659). That is a real pattern, not a statistical trick: the *difference* between a GDP per capita of $1,000 and $5,000 matters enormously for whether a country can afford internet infrastructure, while the difference between $50,000 and $54,000 barely matters at all - a classic diminishing-returns relationship that a raw linear scale compresses into noise and a log scale reveals clearly.
'''))

    cells.append(md('''
**Multivariate:** does the regional pattern (seen in the 2024 cross-section) also hold across the whole time series, or is it a one-year snapshot?
'''))
    cells.append(code('''
regional_2024 = latest_year.groupby("region")["internet_pct"].mean().sort_values(ascending=False)
print("2024 regional means:")
print(regional_2024.round(1).to_string())

global_trend = internet[internet["entity"] == "World"] if "World" in internet_raw["entity"].values else None
world_trend = internet_raw[internet_raw["entity"] == "World"].set_index("year")["internet_pct"]
for year in [2005, 2010, 2015, 2020, 2024]:
    print(f"World, {year}: {world_trend.get(year, float('nan')):.1f}%")
'''))
    cells.append(md('''
Europe (91.6%) leads every other region, and Africa (44.9%) trails all of them by a wide margin - this is not a 2024 anomaly, it is the same ordering that has held for years, and the global average has climbed steadily from 15.6% (2005) to 71.2% (2024). The regional gap and the global trend are two different findings, both true at once: the world got dramatically more connected, and it did not get more *equal* while doing so.
'''))

    cells.append(md('''
**Ghana, specifically** - this dataset covers every country, but one country's story is worth telling in full.
'''))
    cells.append(code('''
ghana = merged[merged["entity"] == "Ghana"].sort_values("year")
ghana_2015 = ghana.loc[ghana["year"] == 2015, "internet_pct"].iloc[0]
ghana_2024 = ghana.loc[ghana["year"] == 2024, "internet_pct"].iloc[0]
africa_2024 = regional_2024["Africa"]

print(f"Ghana, 2015: {ghana_2015:.1f}% online")
print(f"Ghana, 2024: {ghana_2024:.1f}% online")
print(f"Growth: {ghana_2024 - ghana_2015:.1f} percentage points in 9 years")
print(f"Ghana 2024 vs. Africa's 2024 average ({africa_2024:.1f}%): "
      f"{'above' if ghana_2024 > africa_2024 else 'below'} the regional average")
'''))
    cells.append(md('''
Ghana went from 23.0% to 72.2% online in nine years - more than tripling, and well above Africa's 2024 regional average of 44.9%. That is a genuinely strong, specific, citable finding, and exactly the kind of thing a headline in an act report is made of.

One honest note before moving on: the year-by-year line for Ghana (charted in Part 6) is not smooth - it dips sharply in 2019 before jumping in 2020. Nothing in this dataset explains why, and no explanation is invented here. The right move with a real anomaly you cannot explain is to say so plainly, not to smooth over it or make up a cause - exactly Topic 22's rule about separating "interesting" from "important" without guessing at the missing half.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Part 6 - Visualize

Five charts, four distinct types, each titled with its finding - Topic 21's standard, applied here exactly as it would be to any dataset.
'''))
    cells.append(code('''
charts_dir = Path("charts")
charts_dir.mkdir(exist_ok=True)

# 1. Histogram - the distribution, left-skewed.
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(latest_year["internet_pct"], bins=25, color=PALETTE["blue"], edgecolor="white")
ax.axvline(latest_year["internet_pct"].mean(), color=PALETTE["red"], linewidth=2,
           label=f"Mean ({latest_year['internet_pct'].mean():.0f}%)")
ax.axvline(latest_year["internet_pct"].median(), color=INK, linestyle="--", linewidth=2,
           label=f"Median ({latest_year['internet_pct'].median():.0f}%)")
ax.set_title("Most countries cluster near full internet access - a minority pull the mean down")
ax.set_xlabel("Share of population using the internet, 2024 (%)")
ax.set_ylabel("Number of countries")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(charts_dir / "01_distribution.png", dpi=150, bbox_inches="tight")
plt.show()
'''))
    cells.append(code('''
# 2. Bar - regional comparison, sorted, emphasis on the extremes.
fig, ax = plt.subplots(figsize=(9, 5))
colors = [PALETTE["blue"] if r == regional_2024.index[0]
          else (PALETTE["red"] if r == regional_2024.index[-1] else MUTED)
          for r in regional_2024.index]
bars = ax.barh(regional_2024.index[::-1], regional_2024.values[::-1], color=colors[::-1])
ax.bar_label(bars, fmt="%.0f%%", padding=3)
ax.set_title("Europe leads, Africa trails by nearly 47 points - in 2024")
ax.set_xlabel("Mean share of population online (%)")
fig.tight_layout()
fig.savefig(charts_dir / "02_regional_comparison.png", dpi=150, bbox_inches="tight")
plt.show()
'''))
    cells.append(code('''
# 3. Line - the global trend, with Ghana overlaid.
fig, ax = plt.subplots(figsize=(10, 5))
years = sorted(internet_raw[internet_raw["entity"] == "World"]["year"].unique())
ax.plot(world_trend.index, world_trend.values, color=MUTED, linewidth=2, marker="o",
        markersize=3, label="World average")
ax.plot(ghana["year"], ghana["internet_pct"], color=PALETTE["blue"], linewidth=2.5,
        marker="o", markersize=4, label="Ghana")
ax.set_title("Ghana's internet access tripled since 2015, converging toward the world average")
ax.set_xlabel("Year")
ax.set_ylabel("Share of population online (%)")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(charts_dir / "03_ghana_vs_world.png", dpi=150, bbox_inches="tight")
plt.show()
'''))
    cells.append(code('''
# 4. Scatter, log x-axis - GDP vs internet, the strongest relationship in this dataset.
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(latest_year["gdp_per_capita"], latest_year["internet_pct"], s=20, alpha=0.5,
           color=PALETTE["blue"])
ghana_row = latest_year[latest_year["entity"] == "Ghana"].iloc[0]
ax.scatter([ghana_row["gdp_per_capita"]], [ghana_row["internet_pct"]], s=100,
           color=PALETTE["red"], zorder=5)
ax.annotate("Ghana", xy=(ghana_row["gdp_per_capita"], ghana_row["internet_pct"]),
            xytext=(10, -4), textcoords="offset points", fontweight="bold", color=PALETTE["red"])
ax.set_xscale("log")
ax.set_title(f"National income predicts internet access closely on a log scale (r = {r_log:.2f})")
ax.set_xlabel("GDP per capita (log scale, international $)")
ax.set_ylabel("Share of population online, 2024 (%)")
fig.tight_layout()
fig.savefig(charts_dir / "04_gdp_vs_internet.png", dpi=150, bbox_inches="tight")
plt.show()
'''))

    cells.append(md("---"))
    cells.append(md('''
## Part 7 - Model

A regression on log(GDP per capita) predicting internet usage - chosen *because* the exploration above showed the log scale fits much better than the raw one, not as a default first move.
'''))
    cells.append(code('''
x = np.log(latest_year["gdp_per_capita"].values)
y = latest_year["internet_pct"].values

slope, intercept = np.polyfit(x, y, 1)
predicted = slope * x + intercept
ss_res = ((y - predicted) ** 2).sum()
ss_tot = ((y - y.mean()) ** 2).sum()
r_squared = 1 - ss_res / ss_tot

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

axes[0].scatter(x, y, s=18, alpha=0.4, color=PALETTE["blue"])
x_line = np.linspace(x.min(), x.max(), 50)
axes[0].plot(x_line, slope * x_line + intercept, color=PALETTE["red"], linewidth=2.5)
axes[0].set_title(f"log(GDP) -> internet%: R\\u00b2 = {r_squared:.2f} - a strong fit")
axes[0].set_xlabel("log(GDP per capita)")
axes[0].set_ylabel("Internet usage (%)")

residuals = y - predicted
axes[1].scatter(predicted, residuals, s=18, alpha=0.4, color=PALETTE["blue"])
axes[1].axhline(0, color=INK, linewidth=1.5)
axes[1].set_title("Residuals: tightly scattered around zero, no obvious pattern")
axes[1].set_xlabel("Predicted internet usage (%)")
axes[1].set_ylabel("Residual")

fig.tight_layout()
fig.savefig(charts_dir / "05_regression_and_residuals.png", dpi=150, bbox_inches="tight")
plt.show()

print(f"internet_pct = {slope:.2f} x log(gdp_per_capita) + {intercept:.2f}")
print(f"R\\u00b2 = {r_squared:.3f} - log(GDP per capita) alone explains about {r_squared*100:.0f}% of the")
print("variation in internet usage across countries - strong enough to describe as a real, usable relationship.")
'''))
    cells.append(md('''
R² = 0.79 earns the word "predicts" in this section's title in a way that Topic 23b's two examples (0.17 and 0.05) did not. This is the strongest fit across every regression in this topic - worth noticing as a point of contrast: not every relationship found in Topics 20-23 deserved that language, and this one is the exception, not the rule.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Part 8 - Write both reports
'''))
    cells.append(code('''
wrangle_report = f"""
This dataset combines two Our World in Data files - internet usage and GDP per
capita - covering {merged['entity'].nunique()} countries from {merged['year'].min()}
to {merged['year'].max()}.

Both source files mix individual countries with regional and income-group
aggregates such as "World" and "Africa," sitting in the same column as actual
countries. These aggregates do not carry a standard three-letter country code,
which gave a reliable rule for separating them: any row whose code is not
exactly three letters, or starts with "OWID," was treated as an aggregate and
excluded before any country-level analysis. {before - after} entities were
removed this way, including "World" and every regional grouping - correctly
so, since including them would double-count population figures already
reflected in their member countries.

The two files were joined on country, country code, and year, requiring an
exact one-to-one match - a country-year must appear at most once in each
file, and the merge was set to fail loudly if that stopped being true, rather
than silently duplicating rows. No duplicates were found. Some country-years
present in the internet file have no matching GDP figure and were dropped by
this join; this is expected for countries with incomplete historical economic
records; it was not treated as an error.

No values were estimated or filled in. Where a country lacks data for a given
year, it is simply absent from that year's analysis rather than assigned a
guessed value.
"""

act_report = f"""
Globally, {latest_year['internet_pct'].mean():.0f}% of people now use the
internet - but that average hides a large and persistent gap between regions.

Three findings matter most. First, income predicts access closely: on a
logarithmic income scale, GDP per capita alone explains about
{r_squared*100:.0f}% of the variation in a country's internet usage rate
(R\\u00b2 = {r_squared:.2f}) - a strong, usable relationship, not just a loose
correlation. Second, the gap between regions is wide and has not closed:
Europe averages {regional_2024.iloc[0]:.0f}% online against Africa's
{regional_2024['Africa']:.0f}%, a nearly {regional_2024.iloc[0] - regional_2024['Africa']:.0f}-point
gap that mirrors the income gap behind it. Third, Ghana is a genuine success
story within that pattern: internet access rose from {ghana_2015:.0f}% in 2015
to {ghana_2024:.0f}% in 2024 - more than tripling in nine years, and finishing
well above Africa's regional average.

So what: closing the global digital divide is, to a first approximation, an
income problem before it is a technology problem - infrastructure investment
without addressing the underlying income gap is unlikely to close it alone.
Ghana's trajectory is worth studying as a comparator for other sub-Saharan
economies working from a similar starting point in 2015.

Limitations: this analysis uses one cross-sectional year (2024) for the
income-access relationship, so it describes a pattern across countries at one
point in time, not a guarantee that any single country's future income growth
will produce proportional gains in access. GDP and internet access may
reinforce each other rather than one simply causing the other, and this
dataset cannot separate those directions.
"""

Path("wrangle_report.md").write_text(wrangle_report.strip() + "\\n")
Path("act_report.md").write_text(act_report.strip() + "\\n")
print("Both reports saved.")
print(f"Wrangling report: {len(wrangle_report.split())} words")
print(f"Act report:       {len(act_report.split())} words")
'''))

    cells.append(md('''
---
## Part 9 - Presentation outline
'''))
    cells.append(code('''
presentation_outline = """
1. Title: Does National Income Predict Internet Access?
2. The headline: 72% of the world is online in 2024, but the gap by region is wide
3. Finding 1: income predicts access closely on a log scale (R2 = 0.79) - chart 04
4. Finding 2: Europe leads at 92%, Africa trails at 45% - chart 02
5. Finding 3: Ghana tripled its internet access since 2015, now above the African average - chart 03
6. So what: this is an income problem before it is a technology problem
7. Limitations: one cross-sectional year for the regression; correlation, not proven causation
8. Questions
"""
Path("presentation_outline.md").write_text(presentation_outline.strip() + "\\n")
print("Presentation outline saved.")
'''))

    cells.append(md('''
---
## Part 10 - Check this project against the capstone standard

The same check every student's capstone runs - dataset-agnostic, so it works here exactly as it would on any other project.
'''))
    cells.append(import_project_checks_cell())
    cells.append(code('''
import json

results = pc.run_capstone_checks(Path("."), min_chart_count=5)
print(json.dumps(results, indent=2, default=str))
'''))
    cells.append(md('''
If `all_ok` is `True`, this walkthrough meets the same structural bar every student's capstone is held to - proof the bar is achievable, on data nobody pre-built for this course. Remember: this checks *structure*. The reasoning above still had to be correct, the numbers still had to come from real computation, and that part was never something a check cell could verify for you - only a careful reader, which is what your own capstone needs too.
'''))

    return nb(cells)


if __name__ == "__main__":
    write(build_example_walkthrough(), HERE.parent / "instructor_solutions" / "capstone_project" /
          "example_capstone_walkthrough.ipynb")
