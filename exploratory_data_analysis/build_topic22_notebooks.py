"""Generates every Topic 22 (Exploratory Data Analysis) notebook:
  topic22_exploratory_data_analysis.ipynb
  topic22a_asking_good_questions.ipynb .. topic22g_writing_the_act_report.ipynb
  assignments/topic22_assignment_air_quality_eda.ipynb
  ../instructor_solutions/exploratory_data_analysis/topic22_assignment_air_quality_eda_solutions.ipynb

Run: python build_topic22_notebooks.py
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
    """find_data_dir() + palette + load both the air-quality and retail data."""
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
        if (candidate / "air_quality_readings.csv").exists():
            return candidate
    raise FileNotFoundError(
        "Could not find air_quality_readings.csv. Looked in: " +
        ", ".join(str(c) for c in candidates)
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

# The course palette (Topic 21) - fixed hue order, never cycled, so a category
# keeps the same colour in every chart it appears in.
PALETTE = {{
    "blue": "#2a78d6", "aqua": "#1baf7a", "yellow": "#eda100", "green": "#008300",
    "violet": "#4a3aa7", "red": "#e34948", "magenta": "#e87ba4", "orange": "#eb6834",
}}
MUTED = "#c3c2b7"
INK = "#0b0b0b"
STATION_TYPE_COLOR = {{
    "Roadside": PALETTE["red"], "Industrial": PALETTE["orange"],
    "Residential": PALETTE["aqua"], "Background": PALETTE["blue"],
}}
STATION_TYPE_ORDER = ["Roadside", "Industrial", "Residential", "Background"]

WHO_ANNUAL_GUIDELINE = 5.0   # ug/m3, PM2.5 annual mean
WHO_24H_GUIDELINE = 15.0     # ug/m3, PM2.5 24-hour mean

print("pandas version:   ", pd.__version__)
print("data folder:      ", DATA_DIR)
print("files:            ", sorted(p.name for p in DATA_DIR.glob("*.csv")))
'''.rstrip())


def load_air_quality_cell():
    return code('''
stations = pd.read_csv(DATA_DIR / "air_quality_stations.csv")
readings = pd.read_csv(DATA_DIR / "air_quality_readings.csv", parse_dates=["date"])

aq = readings.merge(stations, on="station_id", how="left", validate="m:1")
aq["month"] = aq["date"].dt.month
aq["is_weekend"] = aq["date"].dt.dayofweek.isin([5, 6])
aq["is_harmattan"] = aq["month"].isin([12, 1, 2])

print(f"Air-quality table: {aq.shape[0]} rows x {aq.shape[1]} columns")
print(f"Stations: {aq['station_id'].nunique()}, dates: {aq['date'].min().date()} to {aq['date'].max().date()}")
print(f"Missing pm2_5 readings: {aq['pm2_5'].isna().sum()}")
'''.rstrip())


def rebuild_retail_analysis_cell():
    """Paste Topic 20's build_analysis_table(), for the report-writing sections."""
    return code('''
# The retail "2023 Trading Review" table from Topic 20 - used for the two
# report-writing sections later in this notebook, since a wrangling report and
# an insights report have to be about work you actually did.
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


def footer_cell(back_main, prev, nxt):
    prev_line = f"- Previous: {prev}" if prev else "- Previous: [Main lesson](topic22_exploratory_data_analysis.ipynb)"
    return md(f'''
---
## Where this fits

- [Back to the main lesson]({back_main})
{prev_line}
- Next: {nxt}
'''.rstrip())


def opening_cell(letter, title, scope, section_ref):
    return md(f'''
# Topic 22{letter} - {title}

{scope}

Work through it after reading section {section_ref} of the [main lesson](topic22_exploratory_data_analysis.ipynb).
'''.rstrip())


# ---------------------------------------------------------------------------
# Main lesson: topic22_exploratory_data_analysis.ipynb
# ---------------------------------------------------------------------------

def build_main():
    cells = []

    cells.append(md('''
# Topic 22 - Exploratory Data Analysis

## Knowing what to look for, before you know what you are looking for

Topic 20 wrangled five tables into one. Topic 21 taught you to build any chart correctly, once you already knew what to show. Both of those topics started from a **known question** - "which zone was most profitable," "did revenue grow" - and your job was to answer it accurately.

**Exploratory data analysis (EDA)** is what happens *before* you have a question like that. You have been handed a dataset nobody has looked at yet, and your job is to find out what is in it - what is typical, what is strange, what relates to what - before you know which of those things matters. This is a different skill from the last two topics, and it has its own discipline: a repeatable process for looking, a way of telling a real pattern from noise, and - because EDA is usually worth nothing if nobody else reads it - two distinct ways of writing up what you found.

This lesson uses two datasets. A new one - daily air-quality readings from nine sensors across Accra through 2023 - for the exploration itself, because EDA is only genuine practice on data you have not already seen the answers to. And the retail distributor from Topics 20-21, for the two report types this lesson teaches how to write, because a report about work has to be about work you actually did.
'''))

    cells.append(md('''
## Learning objectives

By the end of this lesson you should be able to:

- describe EDA as a repeatable loop - question, look, visualize, answer or ask a better question - rather than a checklist;
- turn a vague curiosity into a specific, answerable question;
- explore a single variable, a pair of variables, and three or more variables at once, choosing the right view for each;
- tell a real pattern from noise, and an interesting coincidence from an important finding;
- recognise when a strong correlation is a shared cause in disguise, not a relationship between the two things you plotted;
- write a short **wrangling report** that documents data-quality decisions in plain language, for a reader who was not there;
- write a short **insights report** that tells the story of what you found, with visuals, for a reader who wants the finding, not the method.
'''))

    cells.append(md('''
## Wrangling, visualization, and EDA compared

| | Wrangling (Topic 20) | Visualization (Topic 21) | EDA (Topic 22) |
|---|---|---|---|
| Starts from | Several raw tables | One analysis-ready table and a known finding | One table and no question yet |
| Goal | A table that answers questions | A chart that makes one finding unmissable | Finding out which questions are worth asking |
| Mindset | "Is this table trustworthy and the right shape?" | "What is the clearest way to show this?" | "What is actually in here?" |
| Finished when | The table is correct | The chart reads correctly alone | You can say, with evidence, what is and is not interesting |

EDA is not "Topic 21 again, on different data." Topic 21 assumed you already knew the finding and needed the right chart for it. Here, the chart usually comes *first* and is often rough on purpose - you are using it to think, not to present - and the finding comes out the other end, if there is one at all.
'''))

    cells.append(setup_cell("exploratory_data_analysis"))
    cells.append(load_air_quality_cell())

    cells.append(md("---"))
    cells.append(md('''
## What EDA actually is

Every topic before this one was **confirmatory**: you had a specific question, and you wrote code to answer it correctly. EDA is **exploratory**: you do not yet know which questions are worth asking, so the process itself has to help you find out. That process is a loop, not a checklist:

**Ask a question → look at the data → visualize it → get an answer, or a better question → repeat.**

The loop ends not when you run out of questions - you never do - but when you have enough to say something true and useful to someone else. That "write it up" step is not an afterthought tacked on at the end; it is the other half of this lesson, in sections 7 and 8.
'''))
    cells.append(code('''
# A first, deliberately unpolished look - this chart exists to think with, not to present.
fig, ax = plt.subplots(figsize=(10, 4))
daily_mean = aq.groupby("date")["pm2_5"].mean()
ax.plot(daily_mean.index, daily_mean.values, linewidth=1, color=PALETTE["blue"])
ax.set_title("pm2_5 over time, every station averaged - just looking")
plt.show()

print("Two things jump out immediately, before any formal analysis:")
print("  1. A slow rise-and-fall that looks seasonal.")
print("  2. At least one sharp, short spike that does not fit that pattern.")
'''))
    cells.append(md('''
Neither of those is a "finding" yet - a finding needs a number and a cause. But noticing them is what sends you toward the right next question, which is exactly the point of looking before you have a hypothesis.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Asking good questions

"What is going on with air quality in Accra?" is curiosity, not a question you can answer. A question EDA can actually resolve is **specific** (names a variable), **comparative** (names what it is being compared against), and **answerable from the columns you have**.

| Vague | Specific and answerable |
|---|---|
| "Is pollution bad in Accra?" | "What fraction of station-days exceed the WHO 24-hour PM2.5 guideline of 15 ug/m3?" |
| "Does location matter?" | "How does mean PM2.5 differ between Roadside and Background stations?" |
| "Is there a pattern over the year?" | "Is mean PM2.5 higher in December-February than the rest of the year, and by how much?" |
'''))
    cells.append(code('''
pct_exceeding = (aq["pm2_5"] > WHO_24H_GUIDELINE).mean() * 100
print(f"Station-days exceeding the WHO 24-hour guideline ({WHO_24H_GUIDELINE} ug/m3): {pct_exceeding:.1f}%")
'''))
    cells.append(md('''
That single number - computed the moment the vague question became a specific one - is already more useful than a page of charts built before you knew what to ask. Section 22a is entirely practice at this rewriting step.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Univariate exploration: one variable at a time

Start with the shape of a single column before relating it to anything else. `.describe()` gives you five numbers; a histogram shows you the shape those five numbers were summarising.
'''))
    cells.append(code('''
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.hist(aq["pm2_5"].dropna(), bins=50, color=PALETTE["blue"], edgecolor="white")
ax.axvline(WHO_24H_GUIDELINE, color=PALETTE["red"], linewidth=2,
           label=f"WHO 24-hour guideline ({WHO_24H_GUIDELINE} ug/m3)")
ax.axvline(aq["pm2_5"].mean(), color=INK, linewidth=2, linestyle=(0, (4, 2)),
           label=f"Mean ({aq['pm2_5'].mean():.1f} ug/m3)")
ax.set_title("Almost every reading sits above the WHO guideline, not just the worst ones")
ax.set_xlabel("PM2.5 (ug/m3)")
ax.set_ylabel("Number of station-days")
ax.legend(frameon=False)
fig.tight_layout()
plt.show()

print(aq["pm2_5"].describe().round(1).to_string())
print(f"Skew: {aq['pm2_5'].skew():.2f} (right-skewed - a long tail of high readings pulls the mean above the median)")
'''))
    cells.append(md('''
The guideline line is doing real work here: without it, this is just "a right-skewed distribution." With it, the chart says something a reader can act on - the guideline is not a distant ceiling a few bad days bump into, it is close to where the *bulk* of the data already sits.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Bivariate exploration: a pair of variables

Does PM2.5 depend on where you measure, or what the weather is doing? A box plot answers the first (a categorical pair); a scatter plot answers the second (a numeric pair).
'''))
    cells.append(code('''
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

data = [aq.loc[aq["station_type"] == t, "pm2_5"].dropna() for t in STATION_TYPE_ORDER]
bp = axes[0].boxplot(data, tick_labels=STATION_TYPE_ORDER, patch_artist=True)
for patch, t in zip(bp["boxes"], STATION_TYPE_ORDER):
    patch.set_facecolor(STATION_TYPE_COLOR[t])
    patch.set_alpha(0.85)
axes[0].axhline(WHO_24H_GUIDELINE, color=PALETTE["red"], linewidth=1.5, linestyle="--")
axes[0].set_title("Every station type sits above the WHO guideline - even Background")
axes[0].set_ylabel("PM2.5 (ug/m3)")

axes[1].scatter(aq["wind_speed_kmh"], aq["pm2_5"], s=10, alpha=0.3, color=PALETTE["blue"])
r = aq["wind_speed_kmh"].corr(aq["pm2_5"])
axes[1].set_title(f"More wind, less particulate matter (r = {r:.2f})")
axes[1].set_xlabel("Wind speed (km/h)")
axes[1].set_ylabel("PM2.5 (ug/m3)")

fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
Neither chart required a hypothesis going in - you plot the pair because it is plausible, then let the picture tell you whether it was worth plotting. Section 22c practices this on several more pairs, including two that turn out **not** to relate.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Multivariate exploration: three or more at once

Station type and season each affect PM2.5 on their own. Plotting them together answers a sharper question: does the Harmattan bump hit every station type equally, or mostly the already-dirty ones?
'''))
    cells.append(code('''
monthly_by_type = aq.groupby(["month", "station_type"])["pm2_5"].mean().unstack()[STATION_TYPE_ORDER]

fig, ax = plt.subplots(figsize=(10, 5))
for t in STATION_TYPE_ORDER:
    ax.plot(monthly_by_type.index, monthly_by_type[t], marker="o", markersize=4,
            linewidth=2, label=t, color=STATION_TYPE_COLOR[t])
ax.set_title("The Harmattan bump (Dec-Feb) hits every station type, not just the dirty ones")
ax.set_xlabel("Month")
ax.set_ylabel("Mean PM2.5 (ug/m3)")
ax.set_xticks(range(1, 13))
ax.legend(frameon=False)
fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
That is a genuine multivariate finding: two variables (station type, month) combine *additively* rather than one cancelling the other out - Roadside in January is still worse than Background in January, and every type still rises together in Harmattan season. Section 22d goes further, with colour and facets as a third and fourth dimension on one figure.
'''))

    cells.append(md("---"))
    cells.append(md('''
## From patterns to insights

Not everything a scatter plot or a groupby surfaces is worth reporting. Three checks separate a real insight from a false lead:

1. **Sample size.** A dramatic-looking average from three data points is not a pattern - it is three data points.
2. **Correlation versus shared cause.** `pm2_5` and `pm10` correlate at r = 0.99 - but that is because they are two measurements of the same airborne dust, not because one causes the other. A more interesting case: `pm2_5` and `no2` correlate at r = 0.66, not because particulate matter causes nitrogen dioxide, but because both are elevated by the same thing - traffic and industrial activity at Roadside and Industrial stations.
3. **Interesting versus important.** A single extreme day is interesting. Whether it changes what anyone should *do* is a separate question - and answering it usually means finding out whether it was a one-off or the start of a pattern.
'''))
    cells.append(code('''
print("Three correlations with very different explanations:")
print(f"  pm2_5 vs pm10: r = {aq['pm2_5'].corr(aq['pm10']):.2f}  (same phenomenon, measured two ways)")
print(f"  pm2_5 vs no2:  r = {aq['pm2_5'].corr(aq['no2']):.2f}  (shared cause: traffic and industry)")
print(f"  pm2_5 vs temperature: r = {aq['pm2_5'].corr(aq['temperature_c']):.2f}  (both track the dry season)")
'''))
    cells.append(md('''
None of those three numbers is wrong. All three would mislead a reader if reported as "X relates to Y" without the explanation attached. Section 22e practices exactly this: given a candidate finding, decide whether it survives these three checks before it goes in a report.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Writing the wrangling report

Switching datasets here, deliberately: a wrangling report documents work you actually did, and the work you did was Topic 20's retail wrangling, not this lesson's air-quality exploration.

A wrangling report is short (roughly 300-600 words), plain language, and answers exactly three questions: **what problems did you find, what did you do about them, and what should a reader not fully trust as a result?** It is not a code walkthrough - a reader who never sees your notebook should still understand what happened to the data before it reached them.
'''))
    cells.append(rebuild_retail_analysis_cell())
    cells.append(md('''
**A worked example**, built from Topic 20's real, known issues:

> **Wrangling report - 2023 Trading Review**
>
> The distributor's data arrived as six separate files - orders, customers, products, regions, and returns, plus a wide table of monthly targets. Joining them cleanly required fixing three problems first.
>
> The `region` field in the customer list had 47 different spellings of 16 real regions (extra spaces, inconsistent capitalisation, e.g. `"north east"` and `" North East"` for the same region). These were standardised before any join, because an unmatched region silently drops a customer's sales from every regional total.
>
> The product list contained one duplicated product ID, pointing at two different warehouses. Left in place, this would have doubled the sales rows for that product and overstated total revenue. The duplicate was removed, keeping the first listed warehouse.
>
> Finally, 27 of 1,200 orders (2.3%) referenced a customer ID that does not appear in the customer list. These orders could not be assigned a region and were kept - removing them would have understated revenue by GHS 9,090.87 - but they are flagged throughout, and anyone using regional totals should know that 27 orders are not in any region's figure.
>
> With those three fixes applied and checked (every join carries a row-count check that would fail loudly if a fix went wrong), the resulting table is reliable for regional, product, and time-based analysis, with the one stated exception above.

Notice what that example does *not* do: it does not show a single line of code, a column name like `validate="m:1"`, or a DataFrame shape. Every number in it is real, but every sentence is written for someone who has never opened Jupyter.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Writing the act report

The second report answers a different question for a different reader: not "can I trust this data" but "what does it tell us, and so what." Data storytellers use a consistent shape for this: a **hook**, three to five **ranked insights** (each with one chart and a one-line caption that states the finding, not describes the chart), and a closing **so-what** - what should the reader do differently now.
'''))
    cells.append(code('''
# One of the three to five insights a real act report would rank and include.
zone_profit = analysis.groupby("zone")["profit_ghs"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(7, 4))
colors = [PALETTE["blue"] if z == zone_profit.index[0] else MUTED for z in zone_profit.index]
ax.bar(zone_profit.index, zone_profit.values, color=colors)
ax.set_title(f"{zone_profit.index[0]} zone produced the most profit in 2023")
ax.set_ylabel("Profit (GHS)")
fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
**A worked example** of the report this chart would sit inside, built from Topics 20-21's real findings:

> **The 2023 Trading Review, in brief**
>
> The distributor's 2023 revenue (GHS 230,001.08) was not spread evenly across the year, the map, or the product list - and three patterns matter more than the headline total.
>
> **1. Revenue jumped 55.6% in the last two months of the year.** November and December averaged GHS 27,300.78 a month, against GHS 17,539.95 for the rest of the year. Almost all of that jump came from the Middle zone alone, which suggests a seasonal or promotional effect worth planning stock around next year - not a broad trend across the whole business.
>
> **2. The best-margin zone is not the most profitable one.** Middle produced the most total profit (GHS 24,269.81), but Northern converted a larger share of its revenue into profit (29.7% margin against Middle's 28.2%). Growing Northern's volume, not just defending Middle's, may be the better lever.
>
> **3. A third of customers generate 69.2% of all profit.** The top profit tier - 70 of 209 customers - is worth a retention plan of its own; losing a handful of them would hurt more than the raw customer count suggests.
>
> **So what:** plan 2024 stock levels for a Nov-Dec surge concentrated in the Middle zone, investigate what is limiting Northern's volume given its strong margin, and build a specific retention plan for the top profit tier.
>
> *Limitations: this covers 2023 only - there is no prior year to confirm the Nov-Dec pattern repeats. Three customer-profit tiers were drawn from one year of data each.*

Compare this to the wrangling report above. Same underlying work, same author, completely different content: no mention of dirty region strings or duplicate keys - the reader of this report does not need to know the data was ever a problem, only what it now says.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Put it together: one fact, two reports

The clearest way to see why audience changes everything is the same fact, written twice.

| | Wrangling report | Act report |
|---|---|---|
| About | 27 orphan orders with no matching customer | The same 27 orders, now part of the revenue total |
| Says | "27 of 1,200 orders reference an unknown customer and could not be assigned a region; they are kept but flagged." | "2023 revenue was GHS 230,001.08" *(the orphan orders are already inside this number - a reader of the act report does not need to know that)* |
| Reader needs to know | Exactly which numbers to double-check before relying on them | What the business should do next |
| Tone | Precise, hedged, specific about what is uncertain | Confident, narrative, built around a decision |

Neither version is dishonest. The wrangling report's job is to protect a reader who will build on your work; the act report's job is to move a reader who will act on your conclusion. Writing both, about the same work, is the actual skill this lesson is teaching - not writing charts, which Topic 21 already covered.
'''))

    cells.append(md('''
## Key takeaways

- **EDA is a loop, not a checklist**: question, look, visualize, answer or better question, repeat - and it ends when you have something worth writing down, not when you run out of charts to make.
- **A good EDA question is specific, comparative, and answerable** from the columns you actually have.
- **Univariate first, then bivariate, then multivariate** - look at one thing's shape before relating it to another, and relate two things before adding a third.
- **A strong correlation is not evidence of causation**, and is often two measurements of one underlying thing (`pm2_5` and `pm10`, r = 0.99) or two effects of a shared cause (`pm2_5` and `no2`, both driven by traffic and industry).
- **Sample size, shared causes, and "interesting vs. important" are the three checks** a pattern must survive before it becomes a reported finding.
- **A wrangling report** is short, plain-language, and exists to tell a reader exactly what to trust and what to double-check.
- **An act report** is a narrative built around ranked insights and a so-what, aimed at a reader who was never going to open the notebook.
- **The same fact can appear in both reports and sound completely different** - that difference is the skill, not an inconsistency.
'''))

    cells.append(md('''
## Further reading and the course path

### On exploratory data analysis
- [John Tukey, "Exploratory Data Analysis" (1977)](https://www.google.com/search?q=John+Tukey+Exploratory+Data+Analysis+1977) - the book that named this discipline
- [pandas: Essential basic functionality](https://pandas.pydata.org/docs/user_guide/basics.html)

### On writing about data
- [Cole Nussbaumer Knaflic, "Storytelling with Data"](https://www.storytellingwithdata.com/) - the act-report structure this lesson teaches comes from here
- [WHO global air quality guidelines (2021)](https://www.who.int/publications/i/item/9789240034228) - source of the PM2.5 thresholds used throughout this lesson

### Practice notebooks for this topic
- [22a - Asking good questions](topic22a_asking_good_questions.ipynb)
- [22b - Univariate exploration](topic22b_univariate_exploration.ipynb)
- [22c - Bivariate exploration](topic22c_bivariate_exploration.ipynb)
- [22d - Multivariate exploration](topic22d_multivariate_exploration.ipynb)
- [22e - From patterns to insights](topic22e_patterns_to_insights.ipynb)
- [22f - Writing the wrangling report](topic22f_writing_the_wrangling_report.ipynb)
- [22g - Writing the act report](topic22g_writing_the_act_report.ipynb)

### Assignment
- [Topic 22 assignment - Accra air-quality EDA](assignments/topic22_assignment_air_quality_eda.ipynb)

### Elsewhere in the course
- [Topic 20 - Data wrangling](../data_wrangling/topic20_data_wrangling.ipynb)
- [Topic 21 - Data visualization](../data_visualization/topic21_data_visualization.ipynb)
- [Submitting your work with GitHub](../data_analysis_process/topic19d_appendix_submitting_with_github.ipynb)
'''))

    return nb(cells)


# ---------------------------------------------------------------------------
# 22a - Asking good questions
# ---------------------------------------------------------------------------

def build_22a():
    cells = [opening_cell(
        "a", "Asking good questions",
        "The main lesson showed one vague-to-specific rewrite. This notebook practices the skill directly: turning curiosity into questions a column can actually answer, and recognising the four question shapes that map onto the chart types from Topic 21.",
        "2",
    )]
    cells.append(setup_cell("exploratory_data_analysis"))
    cells.append(load_air_quality_cell())

    cells.append(md("---"))
    cells.append(md('''
## The four question shapes

Every answerable EDA question is one of four shapes, and each shape points straight at a Topic 21 chart type:

| Question shape | Example | Chart |
|---|---|---|
| Comparison | "Which station type has the worst PM2.5?" | Bar or box plot |
| Trend | "Did PM2.5 change over the year?" | Line |
| Relationship | "Does wind speed affect PM2.5?" | Scatter |
| Distribution | "What does a typical day's PM2.5 look like, and how much does it vary?" | Histogram or box plot |

Knowing the shape before you write any code tells you which chart to reach for - you are applying Topic 21's chart-selection rule one step earlier than before, to a question you just wrote yourself instead of one someone handed you.
'''))

    cells.append(md('''
### Try It 1 - name the shape

For each question below, name its shape (comparison / trend / relationship / distribution) and the chart you would build:

1. "Is NO2 higher on weekdays than weekends?"
2. "How does PM2.5 vary month to month?"
3. "Is there a relationship between temperature and humidity?"
4. "What is the spread of wind speeds across the whole year?"

Write your four answers as a comment, then pick **one** of the four and actually answer it with code.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(md("---"))
    cells.append(md('''
## Rewriting vague curiosity

A specific question names a **variable**, what it is being **compared against**, and is **answerable from columns you have**. Practice the rewrite on three more vague prompts.
'''))
    cells.append(code('''
vague_prompts = [
    "Is Accra's air quality getting better or worse?",
    "Are industrial areas worse than other places?",
    "Does weather affect pollution?",
]
for p in vague_prompts:
    print("Vague:   ", p)
print()
print("None of these name a time window, a specific comparison, or a specific pollutant.")
print("A rewrite of the first one: 'Was mean PM2.5 in the second half of 2023 higher or")
print("lower than the first half?' - specific, comparative, and answerable from `aq` alone.")
'''))
    cells.append(md('''
### Try It 2 - your own rewrites

Rewrite the second and third vague prompts above into specific, answerable questions, following the same pattern. Then answer both with code.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(md("---"))
    cells.append(md('''
## When a question turns out to be two questions

"Is NO2 higher on weekdays?" looks like one comparison question. It is actually hiding a second one: *is that true everywhere, or only at some station types?* The second version is more useful, because the answer changes what you would recommend.
'''))
    cells.append(code('''
overall = aq.groupby("is_weekend")["no2"].mean()
print("Overall weekday vs weekend NO2:")
print(overall.round(1).to_string())
print()
by_type = aq.groupby(["station_type", "is_weekend"])["no2"].mean().unstack()
by_type.columns = ["Weekday", "Weekend"]
print("Broken down by station type:")
print(by_type.round(1).to_string())
'''))
    cells.append(md('''
The weekday effect holds at every station type here - the gap is not hiding a more interesting split. That is itself worth noting in a report: "this is a citywide pattern, not a one-neighbourhood effect" is a stronger, more useful claim than the first version.
'''))

    cells.append(footer_cell(
        "topic22_exploratory_data_analysis.ipynb", None,
        "[22b - Univariate exploration](topic22b_univariate_exploration.ipynb)",
    ))
    return nb(cells)


# ---------------------------------------------------------------------------
# 22b - Univariate exploration
# ---------------------------------------------------------------------------

def build_22b():
    cells = [opening_cell(
        "b", "Univariate exploration",
        "The main lesson looked at one column, pm2_5. This notebook practices the same move - describe, then visualize - across every numeric column in the air-quality table, plus value_counts for a categorical one, and reading skew correctly.",
        "3",
    )]
    cells.append(setup_cell("exploratory_data_analysis"))
    cells.append(load_air_quality_cell())

    cells.append(md("---"))
    cells.append(md('''
## describe() first, always

Before any chart, `.describe()` tells you the five-number summary and the count - which matters, because a column with missing values will silently describe fewer rows than you expect.
'''))
    cells.append(code('''
for col in ["pm2_5", "pm10", "no2", "temperature_c", "humidity_pct", "wind_speed_kmh"]:
    print(f"--- {col} ---")
    print(aq[col].describe().round(1).to_string())
    print()
'''))
    cells.append(md('''
Every pollutant column shows 3,278 non-null values against 3,285 rows - the seven missing readings from the sensor outages mentioned in the main lesson. The weather columns are complete, because they come from a separate source that was not affected.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Skew tells you whether the mean is trustworthy

A skew near 0 means the mean and median are close, and the mean is a fair "typical value." A skew well above 1 (or below -1) means a handful of extreme values are pulling the mean away from where most of the data actually sits - exactly what happened with `pm2_5` in the main lesson.
'''))
    cells.append(code('''
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

axes[0].hist(aq["no2"].dropna(), bins=30, color=PALETTE["blue"], edgecolor="white")
axes[0].axvline(aq["no2"].mean(), color=PALETTE["red"], linewidth=2, label="Mean")
axes[0].axvline(aq["no2"].median(), color=INK, linestyle="--", linewidth=2, label="Median")
axes[0].set_title(f"no2: skew = {aq['no2'].skew():.2f} - nearly symmetric")
axes[0].legend(frameon=False)

axes[1].hist(aq["pm10"].dropna(), bins=40, color=PALETTE["blue"], edgecolor="white")
axes[1].axvline(aq["pm10"].mean(), color=PALETTE["red"], linewidth=2, label="Mean")
axes[1].axvline(aq["pm10"].median(), color=INK, linestyle="--", linewidth=2, label="Median")
axes[1].set_title(f"pm10: skew = {aq['pm10'].skew():.2f} - right-skewed")
axes[1].legend(frameon=False)

fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
`no2`'s mean and median sit almost on top of each other in the chart; `pm10`'s do not. Reporting "mean PM10" alone, without the shape behind it, would understate how extreme the worst days really get.
'''))

    cells.append(md('''
### Try It 3 - describe a shape in words

Pick `temperature_c` or `humidity_pct`, compute its skew, and write one sentence describing its shape (symmetric, right-skewed, or left-skewed) and whether its mean is a trustworthy "typical value."
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(md("---"))
    cells.append(md('''
## A categorical column: value_counts, not describe

`.describe()` is for numbers. For a categorical column, `.value_counts()` is the univariate view - and the *count* itself can be a finding, before you even look at any pollutant value.
'''))
    cells.append(code('''
print(aq["station_type"].value_counts().to_string())
print()
print("Residential and Roadside each have three stations (1,095 station-days); Industrial has")
print("two (730); Background has one (365). Any comparison across station types is therefore")
print("comparing unequal amounts of data - worth remembering before ranking them with confidence.")
'''))

    cells.append(md('''
### Try It 4 - your own univariate pass

Choose any column in `aq` not yet explored in this notebook, run `.describe()` or `.value_counts()` as appropriate, build one chart, and write one sentence stating what is typical and what, if anything, is unusual.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(footer_cell(
        "topic22_exploratory_data_analysis.ipynb",
        "[22a - Asking good questions](topic22a_asking_good_questions.ipynb)",
        "[22c - Bivariate exploration](topic22c_bivariate_exploration.ipynb)",
    ))
    return nb(cells)


# ---------------------------------------------------------------------------
# 22c - Bivariate exploration
# ---------------------------------------------------------------------------

def build_22c():
    cells = [opening_cell(
        "c", "Bivariate exploration",
        "The main lesson looked at one categorical pair (station type) and one numeric pair (wind speed). This notebook practices more pairs - including two that turn out not to relate, which is just as important a result as one that does.",
        "4",
    )]
    cells.append(setup_cell("exploratory_data_analysis"))
    cells.append(load_air_quality_cell())

    cells.append(md("---"))
    cells.append(md('''
## Two numeric variables that barely relate

Not every plausible pair is actually related. `no2` and `wind_speed_kmh` are worth checking - wind disperses particulates, so might it disperse NO2 too?
'''))
    cells.append(code('''
r = aq["wind_speed_kmh"].corr(aq["no2"])
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(aq["wind_speed_kmh"], aq["no2"], s=10, alpha=0.3, color=PALETTE["blue"])
ax.set_title(f"Wind speed barely affects NO2 (r = {r:.2f}) - unlike PM2.5 (r = -0.27)")
ax.set_xlabel("Wind speed (km/h)")
ax.set_ylabel("NO2 (ug/m3)")
fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
That near-zero correlation is a real finding, not a failed chart. NO2 comes mostly from combustion (traffic, generators) right at the point of measurement; it does not travel and disperse the way airborne dust does, so wind has much less effect on it than it does on PM2.5. The *difference* between the two r-values (-0.27 vs -0.01) is more informative than either one alone.
'''))

    cells.append(md("---"))
    cells.append(md('''
## A categorical pair: does the weekday effect hold everywhere?

The main lesson found weekday NO2 higher than weekend NO2 overall. Is that one citywide pattern, or does it only show up at certain station types?
'''))
    cells.append(code('''
by_type = aq.groupby(["station_type", "is_weekend"])["no2"].mean().unstack()
by_type.columns = ["Weekday", "Weekend"]
by_type = by_type.loc[STATION_TYPE_ORDER]
by_type["gap_pct"] = ((by_type["Weekday"] / by_type["Weekend"] - 1) * 100).round(1)

fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(STATION_TYPE_ORDER))
width = 0.35
ax.bar(x - width/2, by_type["Weekday"], width, label="Weekday", color=PALETTE["blue"])
ax.bar(x + width/2, by_type["Weekend"], width, label="Weekend", color=MUTED)
ax.set_xticks(x)
ax.set_xticklabels(STATION_TYPE_ORDER)
ax.set_title("The weekday NO2 gap holds at every station type")
ax.set_ylabel("Mean NO2 (ug/m3)")
ax.legend(frameon=False)
fig.tight_layout()
plt.show()

print(by_type.round(1).to_string())
'''))
    cells.append(md('''
It holds everywhere, with a similar roughly 30% gap at each type. That is a stronger claim than the citywide average alone: "the weekday effect is consistent across every kind of location," not just true on average.
'''))

    cells.append(md('''
### Try It 5 - a confounded pair

Plot `pm2_5` against `humidity_pct`. You will find a negative correlation. Before concluding "humidity reduces particulate matter," check: does humidity also correlate with `month` or with the Harmattan season? Write one sentence about what is really driving the relationship you see.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(footer_cell(
        "topic22_exploratory_data_analysis.ipynb",
        "[22b - Univariate exploration](topic22b_univariate_exploration.ipynb)",
        "[22d - Multivariate exploration](topic22d_multivariate_exploration.ipynb)",
    ))
    return nb(cells)


# ---------------------------------------------------------------------------
# 22d - Multivariate exploration
# ---------------------------------------------------------------------------

def build_22d():
    cells = [opening_cell(
        "d", "Multivariate exploration",
        "The main lesson combined station type and month on one line chart. This notebook adds a heatmap grid (two categorical dimensions at once, reusing Topic 21's sequential-colour rule) and a three-variable scatter using colour as the third dimension.",
        "5",
    )]
    cells.append(setup_cell("exploratory_data_analysis"))
    cells.append(load_air_quality_cell())

    cells.append(md("---"))
    cells.append(md('''
## A heatmap: two categorical dimensions, one number

Station type and season each matter on their own (the main lesson's line chart showed both at once). A heatmap of month x station type shows the same two dimensions in a different, often faster-to-scan shape - exactly the sequential-colour heatmap from Topic 21e, since this is a magnitude grid, not a correlation.
'''))
    cells.append(code('''
grid = aq.groupby(["station_type", "month"])["pm2_5"].mean().unstack()[range(1, 13)].loc[STATION_TYPE_ORDER]

fig, ax = plt.subplots(figsize=(11, 4.5))
im = ax.imshow(grid.values, cmap="Reds", aspect="auto")
ax.set_xticks(range(12))
ax.set_xticklabels(range(1, 13))
ax.set_yticks(range(len(STATION_TYPE_ORDER)))
ax.set_yticklabels(STATION_TYPE_ORDER)
ax.set_xlabel("Month")
ax.set_title("Every station type peaks in January - the grid confirms the line chart")
fig.colorbar(im, ax=ax, shrink=0.85, label="Mean PM2.5 (ug/m3)")
fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
This is the same information as the main lesson's line chart, in a different shape. Neither is "more correct" - the line chart makes the *trend* easier to see, the heatmap makes the *full grid of 48 numbers* easier to scan at once. Part of multivariate exploration is trying more than one shape before deciding which belongs in a report.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Three variables on one scatter: position and colour

A scatter plot has two positional axes. Colour can carry a third variable - here, whether each day falls in Harmattan season - on top of the wind/PM2.5 relationship from Topic 22c.
'''))
    cells.append(code('''
fig, ax = plt.subplots(figsize=(9, 6))
for is_harmattan, color, label in [(False, PALETTE["blue"], "Rest of year"),
                                     (True, PALETTE["red"], "Harmattan (Dec-Feb)")]:
    subset = aq[aq["is_harmattan"] == is_harmattan]
    ax.scatter(subset["wind_speed_kmh"], subset["pm2_5"], s=10, alpha=0.35,
               color=color, label=label)
ax.set_title("Harmattan days (red) sit higher at every wind speed, not just on calm days")
ax.set_xlabel("Wind speed (km/h)")
ax.set_ylabel("PM2.5 (ug/m3)")
ax.legend(frameon=False)
fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
If Harmattan's effect were just "it happens to be calmer in Harmattan season," the red points would cluster at low wind speeds only. Instead they sit above the blue points across the *whole* wind-speed range - evidence that the Harmattan effect is a real, separate factor, not an artefact of the wind/PM2.5 relationship you already found.
'''))

    cells.append(md('''
### Try It 6 - facet by station type

Using `plt.subplots(2, 2, ...)`, build one small scatter of wind speed vs. PM2.5 per station type (one panel per type, same axis limits on every panel so they are visually comparable). Does the wind effect look equally strong at every station type, or stronger at some than others?
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(footer_cell(
        "topic22_exploratory_data_analysis.ipynb",
        "[22c - Bivariate exploration](topic22c_bivariate_exploration.ipynb)",
        "[22e - From patterns to insights](topic22e_patterns_to_insights.ipynb)",
    ))
    return nb(cells)


# ---------------------------------------------------------------------------
# 22e - From patterns to insights
# ---------------------------------------------------------------------------

def build_22e():
    cells = [opening_cell(
        "e", "From patterns to insights",
        "The main lesson stated three checks for a candidate finding: sample size, shared cause, interesting vs. important. This notebook applies them to two real anomaly events hiding in the air-quality data, and to a set of candidate findings you have to accept or reject.",
        "6",
    )]
    cells.append(setup_cell("exploratory_data_analysis"))
    cells.append(load_air_quality_cell())

    cells.append(md("---"))
    cells.append(md('''
## A mystery: one station, or the whole city?

Back in the main lesson's very first chart, a sharp short spike was visible in the citywide average. Here it is again, isolated and dated.
'''))
    cells.append(code('''
daily = aq.groupby("date")["pm2_5"].mean()
spike_day = daily.idxmax()
print(f"Citywide daily average peaks on {spike_day.date()}, at {daily.max():.1f} ug/m3")
print(f"(The surrounding days average {daily.drop(spike_day).loc['2023-03-15':'2023-03-29'].mean():.1f}.)")
'''))
    cells.append(md('''
Is that a single malfunctioning sensor, or something that actually happened across the city? One groupby answers it.
'''))
    cells.append(code('''
around_spike = aq[aq["date"].between("2023-03-20", "2023-03-25")]
pivot = around_spike.pivot_table(index="date", columns="station_name", values="pm2_5")

fig, ax = plt.subplots(figsize=(11, 5))
for col in pivot.columns:
    ax.plot(pivot.index, pivot[col], marker="o", markersize=4, linewidth=1.5, label=col, alpha=0.8)
ax.set_title("Every station spikes on the same two days - this is citywide, not one sensor")
ax.set_ylabel("PM2.5 (ug/m3)")
ax.legend(frameon=False, fontsize=7, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12))
fig.tight_layout()
plt.show()
'''))
    cells.append(md('''
Every one of the nine lines rises on the same two days. That rules out a single faulty sensor - whatever happened on 22-23 March affected the whole city at once, which points toward a weather event (a short, severe dust intrusion outside the normal Harmattan window) rather than anything local to one neighbourhood.
'''))

    cells.append(md("---"))
    cells.append(md('''
## A second mystery: the same question, opposite answer

The main lesson's industrial-zone figures hid a second spike, in June - outside Harmattan season entirely. Same investigative method, different answer.
'''))
    cells.append(code('''
june_window = aq[aq["date"].between("2023-06-08", "2023-06-14")]
pivot2 = june_window.pivot_table(index="date", columns="station_name", values="pm2_5")

fig, ax = plt.subplots(figsize=(11, 5))
for col in pivot2.columns:
    style = {"linewidth": 3, "alpha": 1.0} if col == "Tema Industrial Area" else {"linewidth": 1, "alpha": 0.4}
    color = PALETTE["red"] if col == "Tema Industrial Area" else MUTED
    ax.plot(pivot2.index, pivot2[col], marker="o", markersize=4, color=color, label=col, **style)
ax.set_title("Only Tema Industrial Area spikes in June - this one IS local")
ax.set_ylabel("PM2.5 (ug/m3)")
ax.legend(frameon=False, fontsize=7, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12))
fig.tight_layout()
plt.show()

normal = aq[(aq["station_name"] == "Tema Industrial Area") & aq["date"].between("2023-06-01", "2023-06-09")]["pm2_5"].mean()
peak = aq[(aq["station_name"] == "Tema Industrial Area") & aq["date"].between("2023-06-10", "2023-06-12")]["pm2_5"].max()
print(f"Tema Industrial Area: normal ~{normal:.1f} ug/m3, peaks at {peak:.1f} ug/m3 ({peak/normal:.1f}x) on 10-12 June")
'''))
    cells.append(md('''
Same visual method, opposite conclusion: this spike sits on top of one line, not all nine. That single difference - citywide versus single-station - is usually enough to tell a weather event from an equipment fault or a local incident, before you ever need an external news report to confirm it.
'''))

    cells.append(md("---"))
    cells.append(md('''
## Accept or reject: five candidate findings

A colleague hands you five "findings" from a first pass over this data. Apply the three checks from the main lesson - sample size, shared cause, interesting vs. important - to each, and say which you would actually put in a report.

1. "Aburi Background Site had its single highest reading on a Tuesday - Tuesdays must be worse for air quality."
2. "PM2.5 and PM10 correlate at r = 0.99, so reducing one will reduce the other."
3. "Roadside stations average 63.9 ug/m3 against Background's 17.7 - location matters more than weather."
4. "Industrial stations' NO2 (27.9) is lower than Roadside's (35.2), so industrial activity matters less than traffic."
5. "The two anomaly events in this dataset prove Accra's air quality is getting worse."
'''))
    cells.append(code('''
# YOUR CODE HERE
# For each of the five, write accept/reject and one sentence of reasoning.
'''))
    cells.append(md('''
A hint on two of the five: (1) one single data point is never a day-of-week pattern - that is sample size. (5) two specific, dated events are evidence of two events, not of a trend - generalising from them to "getting worse" needs many more years of data than this dataset has.
'''))

    cells.append(footer_cell(
        "topic22_exploratory_data_analysis.ipynb",
        "[22d - Multivariate exploration](topic22d_multivariate_exploration.ipynb)",
        "[22f - Writing the wrangling report](topic22f_writing_the_wrangling_report.ipynb)",
    ))
    return nb(cells)


# ---------------------------------------------------------------------------
# 22f - Writing the wrangling report
# ---------------------------------------------------------------------------

def build_22f():
    cells = [opening_cell(
        "f", "Writing the wrangling report",
        "The main lesson showed one complete worked wrangling report. This notebook gives you a checklist for judging one, a bad-versus-good comparison, and practice writing your own paragraph about a Topic 20 decision the worked example did not cover.",
        "7",
    )]
    cells.append(setup_cell("exploratory_data_analysis"))
    cells.append(rebuild_retail_analysis_cell())

    cells.append(md("---"))
    cells.append(md('''
## A checklist for a wrangling report

A wrangling report earns its keep if, and only if, a reader who never opens the notebook could still answer three questions from it alone:

- [ ] What problems were in the raw data?
- [ ] What was done about each one?
- [ ] What should the reader still not fully trust?

And it fails on tone if it does any of these:
- [ ] Shows code, a column name, or a library function name
- [ ] Uses the word "just" to describe a decision with a real trade-off ("I just dropped the bad rows")
- [ ] States a fix without a number attached (how many rows, what percentage)
'''))

    cells.append(md("---"))
    cells.append(md('''
## Bad versus good, same issue

Here is the orphan-order issue from the main lesson's worked example, written badly first.
'''))
    cells.append(md('''
> **Bad:** "I ran a left join on customer_id and found some nulls in the region column, which I kept in the DataFrame after checking `isna().sum()`. There were 27 of them."

This is accurate and still a bad wrangling report. It assumes the reader knows what a left join is, states a number with no context for whether 27 is a lot, and never says what a reader should actually do about it.

> **Good:** "27 of the distributor's 1,200 orders (2.3%) came from a customer who is not in the customer list - likely a data-entry error when the order was logged. These orders are kept, because removing them would understate 2023 revenue by GHS 9,090.87, but they cannot be assigned to a region. Anyone using regional totals should know that 2.3% of revenue sits outside every region's figure."

Same fact, same number, completely different report. The second version never mentions pandas and is more useful to a non-technical reader than the first.
'''))

    cells.append(md('''
### Try It 7 - write your own paragraph

Topic 20 also found that `targets_wide.csv` needed melting from wide to long format before it could be joined - a reshaping decision, not a data-quality fix, but still something a wrangling report should mention if it changed what a reader can trust about the targets. Write one paragraph (3-5 sentences, no code, no column names) explaining this decision to someone who has never seen the file. Then check it against the checklist above.
'''))
    cells.append(code('''
my_paragraph = """
YOUR PARAGRAPH HERE
"""

word_count = len(my_paragraph.split())
print(f"Word count: {word_count}")
print(f"Contains no code-like text (no underscores, no parentheses): "
      f"{'_' not in my_paragraph and '(' not in my_paragraph}")
'''))

    cells.append(footer_cell(
        "topic22_exploratory_data_analysis.ipynb",
        "[22e - From patterns to insights](topic22e_patterns_to_insights.ipynb)",
        "[22g - Writing the act report](topic22g_writing_the_act_report.ipynb)",
    ))
    return nb(cells)


# ---------------------------------------------------------------------------
# 22g - Writing the act report (pure consolidation, no new teaching)
# ---------------------------------------------------------------------------

def build_22g():
    cells = [md('''
# Topic 22g - Writing the act report

A consolidation notebook. Everything here uses the whole Topic 22 toolkit and gives you no worked answers - only the checks that tell you whether your answer is right.

Work through the [main lesson](topic22_exploratory_data_analysis.ipynb) and notebooks 22a to 22f first.

## The scenario

The managing director liked the dashboard from Topic 21. Now she wants the written version - a one-page act report she can forward to the board without attaching a notebook. Five candidate findings are below, computed from angles the rest of this topic did not already use. Your job: rank them, pick the ones worth reporting, and write the report.
''')]
    cells.append(setup_cell("exploratory_data_analysis"))
    cells.append(rebuild_retail_analysis_cell())

    cells.append(md("---"))
    cells.append(md('''
## Task 1 - Compute the five candidates

Run each of the five groupbys below and print the result. Do not interpret them yet.

1. Revenue by individual product (`product_name`), top 5
2. Return rate by individual product (`was_returned` mean x 100), sorted worst first, with each product's order count alongside
3. Revenue share by channel (percentage of total)
4. Order count by weekday
5. Monthly revenue by zone (the pivot you would need for a line chart)
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(md('''
## Task 2 - Apply the three checks

For each of the five candidates, apply the checks from 22e (sample size, shared cause, interesting vs. important) and decide: report it, or leave it out. Write one line per candidate.

(Hint: one of the five has a sample-size problem worth naming explicitly - a product with only 20-30 orders total can show a dramatic-looking return *rate* that is actually 7-9 returns.)
'''))
    cells.append(code('''
# YOUR CODE HERE
# decisions = {"candidate 1": "report" or "leave out", ...}  with a one-line reason each
'''))

    cells.append(md('''
## Task 3 - One chart per chosen insight

For each candidate you decided to report, build one chart - the right type for that question, per the chart-selection rule. Give each one a title that states the finding.
'''))
    cells.append(code("# YOUR CODE HERE"))

    cells.append(md("---"))
    cells.append(md('''
## Task 4 - Write the act report

Using the hook / ranked insights / so-what / limitations structure from the main lesson, write the full report as a Python string. Required:

- a one-sentence hook naming the overall headline number;
- 3-4 insights, each with at least one specific number;
- a "So what" paragraph naming at least one concrete action;
- a "Limitations" line.
'''))
    cells.append(code('''
act_report = """
YOUR REPORT HERE
"""
'''))

    cells.append(md('''
## Task 5 - Self-check your own report in code

Word count and section presence are things code can check, even though the writing quality itself cannot be. Run this cell against your `act_report`.
'''))
    cells.append(code('''
import re

word_count = len(act_report.split())
numbers_found = len(re.findall(r"\\d[\\d,]*\\.?\\d*", act_report))
has_so_what = "so what" in act_report.lower()
has_limitations = "limitation" in act_report.lower()

print(f"Word count: {word_count} (aim for roughly 150-350)")
print(f"Distinct numeric figures mentioned: {numbers_found} (aim for at least 5)")
print(f"Has a So What section: {has_so_what}")
print(f"Has a Limitations section: {has_limitations}")
'''))

    cells.append(md('''
## Self-check

- [ ] All five candidates computed before any were judged - you did not skip straight to the ones that looked interesting
- [ ] The sample-size problem (a rate computed from very few orders) was caught and named, not reported as fact
- [ ] Every chosen insight has one chart, titled with the finding, not a generic label
- [ ] The report has a hook, 3-4 insights, a So What, and a Limitations line
- [ ] At least 5 distinct numbers appear in the report text
- [ ] No chart used is a pie or waffle with more than 5 slices
- [ ] No `# YOUR CODE HERE` remains anywhere

---
## Where this fits

- [Back to the main lesson](topic22_exploratory_data_analysis.ipynb)
- Previous: [22f - Writing the wrangling report](topic22f_writing_the_wrangling_report.ipynb)
- Next: [Topic 22 assignment](assignments/topic22_assignment_air_quality_eda.ipynb)
'''))
    return nb(cells)


if __name__ == "__main__":
    write(build_main(), HERE / "topic22_exploratory_data_analysis.ipynb")
    write(build_22a(), HERE / "topic22a_asking_good_questions.ipynb")
    write(build_22b(), HERE / "topic22b_univariate_exploration.ipynb")
    write(build_22c(), HERE / "topic22c_bivariate_exploration.ipynb")
    write(build_22d(), HERE / "topic22d_multivariate_exploration.ipynb")
    write(build_22e(), HERE / "topic22e_patterns_to_insights.ipynb")
    write(build_22f(), HERE / "topic22f_writing_the_wrangling_report.ipynb")
    write(build_22g(), HERE / "topic22g_writing_the_act_report.ipynb")


# ---------------------------------------------------------------------------
# Assignment + instructor solutions: shared text and check cells
# ---------------------------------------------------------------------------

ASSIGNMENT_TITLE = "# Topic 22 Assignment - The Accra Air-Quality EDA"

ASSIGNMENT_SCENARIO = '''
## Scenario

A city-council contact has handed you a year of 2023 daily sensor readings from five air-quality stations you have never seen before - different neighbourhoods from the ones in the lesson. She wants two things, exactly like Topic 22 taught: can the data be trusted, and what does it say. Nobody on the council will open your notebook, so both answers have to stand alone as writing.

### What you are practising

| Skill | Where |
|---|---|
| First-look inspection of a new dataset | Part 1 |
| Univariate exploration and reading skew | Part 2 |
| Bivariate exploration (categorical and numeric pairs) | Part 3 |
| Multivariate exploration (season x weekday effects) | Part 4 |
| Investigating an anomaly: one station or citywide? | Part 5 |
| Checking a finding against a real guideline threshold | Part 6 |
| Writing a wrangling report | Part 7 |
| Writing an act report | Part 8 |
| Submitting work with Git and GitHub | Part 10 |
'''

ASSIGNMENT_SUBMIT = '''
## What you must submit

A **public** GitHub repository named **`itfy-air-quality-eda`** containing:

1. this notebook, completed, **run from top to bottom so every output is visible**;
2. `data/` - the two source CSVs, unchanged;
3. `charts/` - every chart you built, saved;
4. `wrangle_report.md` - your wrangling report, as its own file;
5. `act_report.md` - your act report, as its own file, with at least one chart image embedded (Markdown: `![caption](charts/filename.png)`).

Full submission instructions are in [the GitHub submission guide](../../data_analysis_process/topic19d_appendix_submitting_with_github.ipynb).

### Rules

- **Complete every function skeleton.** A loose answer in a cell instead of a completed function loses that part's marks.
- **Both reports must pass their own check cell** (word count, required sections, numeric-claim count) **and** read naturally - a report that passes the check but reads like a code comment still loses marks.
- **The wrangling report contains no code, column names, or library names.** If you would not say it out loud to someone who has never used pandas, rewrite it.
- **Every chart needs a title that states a finding, axis labels with units, and a legend if it has more than one series.**
- **Never claim a citywide pattern from one station, or a trend from one dated event.**
'''

ASSIGNMENT_HOWTO = '''
## How to work through this notebook

Replace every `# TODO n` with your code, and delete each `raise NotImplementedError(...)` once the function works. The check cell beneath each part compares against figures computed from the real data - a `False` means your code is wrong, not the check.

Work in order. This is a different set of stations from the lesson - do not assume the lesson's numbers apply here.
'''

PART1_MD = '''
## Part 1 - First look

Write `load_and_inspect(data_dir)`, returning `(aq, summary)` where `aq` is the merged readings+stations table (with `month`, `is_weekend`, `is_harmattan` columns added, exactly as the lesson's `load_air_quality_cell` did) and `summary` is a dict with keys `"n_rows"`, `"n_stations"`, `"missing_pm25"`.
'''

PART1_TODO = '''
def load_and_inspect(data_dir):
    """Load the assignment's air-quality tables, merge, and summarise."""
    # TODO 1: read air_quality_readings_assignment.csv and air_quality_stations_assignment.csv.
    # TODO 2: merge, add month / is_weekend / is_harmattan columns (same as the lesson).
    # TODO 3: build the summary dict and return (aq, summary).
    raise NotImplementedError("Complete this function, then delete this line.")


aq, summary = load_and_inspect(DATA_DIR)
print(summary)
'''

PART1_SOLUTION = '''
def load_and_inspect(data_dir):
    """Load the assignment's air-quality tables, merge, and summarise."""
    stations = pd.read_csv(data_dir / "air_quality_stations_assignment.csv")
    readings = pd.read_csv(data_dir / "air_quality_readings_assignment.csv", parse_dates=["date"])
    aq = readings.merge(stations, on="station_id", how="left", validate="m:1")
    aq["month"] = aq["date"].dt.month
    aq["is_weekend"] = aq["date"].dt.dayofweek.isin([5, 6])
    aq["is_harmattan"] = aq["month"].isin([12, 1, 2])
    summary = {
        "n_rows": len(aq),
        "n_stations": aq["station_id"].nunique(),
        "missing_pm25": int(aq["pm2_5"].isna().sum()),
    }
    return aq, summary


aq, summary = load_and_inspect(DATA_DIR)
print(summary)
'''

CHECK1 = '''
# Check cell. All must print True.
print("1825 rows:    ", summary["n_rows"] == 1825)
print("5 stations:   ", summary["n_stations"] == 5)
print("5 missing:    ", summary["missing_pm25"] == 5)
'''

PART2_MD = '''
---
## Part 2 - Ask three specific questions

Before exploring, write three questions about this new dataset, following the "specific, comparative, answerable" rule from 22a. At least one must be a comparison question and at least one must be a relationship question.
'''

PART2_ANSWER_MD = '''
**Your three questions:**

1. *(question)*
2. *(question)*
3. *(question)*
'''

PART3_MD = '''
---
## Part 3 - Univariate: the shape of PM2.5

Write `describe_pm25(aq)`, returning a dict with keys `"mean"`, `"median"`, `"skew"` (all rounded to 2 decimal places), for the `pm2_5` column.
'''

PART3_TODO = '''
def describe_pm25(aq):
    # TODO 4: compute mean, median, and skew of pm2_5, rounded to 2dp, as a dict.
    raise NotImplementedError("Complete this function, then delete this line.")


pm25_shape = describe_pm25(aq)
print(pm25_shape)
'''

PART3_SOLUTION = '''
def describe_pm25(aq):
    return {
        "mean": round(aq["pm2_5"].mean(), 2),
        "median": round(aq["pm2_5"].median(), 2),
        "skew": round(aq["pm2_5"].skew(), 2),
    }


pm25_shape = describe_pm25(aq)
print(pm25_shape)
'''

CHECK3 = '''
# Check cell. Must print True.
print("mean > median (right-skewed):", pm25_shape["mean"] > pm25_shape["median"])
print("skew > 1:                    ", pm25_shape["skew"] > 1)
'''

PART4_MD = '''
---
## Part 4 - Bivariate: station type and wind

Write `pm25_by_station_type(aq)` returning a Series of mean `pm2_5` by `station_type`, sorted descending. Separately, write `wind_pm25_correlation(aq)` returning the correlation coefficient, rounded to 2dp.
'''

PART4_TODO = '''
def pm25_by_station_type(aq):
    # TODO 5: groupby station_type, mean pm2_5, sort descending.
    raise NotImplementedError("Complete this function, then delete this line.")


def wind_pm25_correlation(aq):
    # TODO 6: correlation between wind_speed_kmh and pm2_5, rounded to 2dp.
    raise NotImplementedError("Complete this function, then delete this line.")


station_type_means = pm25_by_station_type(aq)
wind_corr = wind_pm25_correlation(aq)
print(station_type_means.round(1))
print("wind correlation:", wind_corr)
'''

PART4_SOLUTION = '''
def pm25_by_station_type(aq):
    return aq.groupby("station_type")["pm2_5"].mean().sort_values(ascending=False)


def wind_pm25_correlation(aq):
    return round(aq["wind_speed_kmh"].corr(aq["pm2_5"]), 2)


station_type_means = pm25_by_station_type(aq)
wind_corr = wind_pm25_correlation(aq)
print(station_type_means.round(1))
print("wind correlation:", wind_corr)
'''

CHECK4 = '''
# Check cell. All must print True.
print("Roadside is worst:   ", station_type_means.index[0] == "Roadside")
print("Background is best:  ", station_type_means.index[-1] == "Background")
print("sorted descending:   ", list(station_type_means) == sorted(station_type_means, reverse=True))
print("wind correlation < 0:", wind_corr < 0)
'''

PART5_MD = '''
---
## Part 5 - Multivariate: season and weekday effects

Write `seasonal_and_weekday_effects(aq)` returning a dict with keys `"harmattan_pct_higher"` (how much higher mean PM2.5 is in Dec-Feb vs. the rest of the year, as a percentage, rounded to 1dp) and `"no2_weekday_pct_higher"` (the same calculation for NO2, weekday vs. weekend).
'''

PART5_TODO = '''
def seasonal_and_weekday_effects(aq):
    # TODO 7: harmattan mean vs rest-of-year mean for pm2_5, as a % difference.
    # TODO 8: weekday mean vs weekend mean for no2, as a % difference.
    raise NotImplementedError("Complete this function, then delete this line.")


effects = seasonal_and_weekday_effects(aq)
print(effects)
'''

PART5_SOLUTION = '''
def seasonal_and_weekday_effects(aq):
    harmattan_mean = aq[aq["is_harmattan"]]["pm2_5"].mean()
    rest_mean = aq[~aq["is_harmattan"]]["pm2_5"].mean()
    no2_weekday = aq[~aq["is_weekend"]]["no2"].mean()
    no2_weekend = aq[aq["is_weekend"]]["no2"].mean()
    return {
        "harmattan_pct_higher": round((harmattan_mean / rest_mean - 1) * 100, 1),
        "no2_weekday_pct_higher": round((no2_weekday / no2_weekend - 1) * 100, 1),
    }


effects = seasonal_and_weekday_effects(aq)
print(effects)
'''

CHECK5 = '''
# Check cell. Both must print True.
print("Harmattan effect is positive and real:  ", 20 < effects["harmattan_pct_higher"] < 70)
print("Weekday NO2 effect is positive and real:", 15 < effects["no2_weekday_pct_higher"] < 55)
'''

PART6_MD = '''
---
## Part 6 - Investigate the anomaly

Somewhere in this year there is at least one multi-day spike well outside the normal range. Write `find_anomaly_dates(aq, threshold=90)`, returning a sorted list of dates (as strings) where the **citywide mean** `pm2_5` exceeds `threshold`. Then write `is_citywide(aq, date, margin=1.5)`, returning `True` if **every** station's reading on that date exceeds `margin` times its own annual mean (i.e. the event is not isolated to one station).
'''

PART6_TODO = '''
def find_anomaly_dates(aq, threshold=90):
    # TODO 9: citywide daily mean pm2_5, dates where it exceeds threshold, as sorted strings.
    raise NotImplementedError("Complete this function, then delete this line.")


def is_citywide(aq, date, margin=1.5):
    # TODO 10: for the given date, compare each station's reading to `margin` times
    #          that station's own annual mean pm2_5. Return True only if ALL exceed it.
    raise NotImplementedError("Complete this function, then delete this line.")


anomaly_dates = find_anomaly_dates(aq)
citywide_flags = {d: is_citywide(aq, d) for d in anomaly_dates}
print("Anomaly dates:", anomaly_dates)
print("Citywide?     ", citywide_flags)
'''

PART6_SOLUTION = '''
def find_anomaly_dates(aq, threshold=90):
    daily = aq.groupby("date")["pm2_5"].mean()
    return sorted(d.strftime("%Y-%m-%d") for d in daily.index[daily > threshold])


def is_citywide(aq, date, margin=1.5):
    station_avg = aq.groupby("station_id")["pm2_5"].mean()
    day = aq[aq["date"] == date].set_index("station_id")["pm2_5"]
    return bool((day > margin * station_avg).all())


anomaly_dates = find_anomaly_dates(aq)
citywide_flags = {d: is_citywide(aq, d) for d in anomaly_dates}
print("Anomaly dates:", anomaly_dates)
print("Citywide?     ", citywide_flags)
'''

CHECK6 = '''
# Check cell. All must print True.
print("found both event days:  ", set(anomaly_dates) == {"2023-07-14", "2023-07-15"})
print("both flagged citywide:  ", all(citywide_flags.values()))
'''

PART7_MD = '''
---
## Part 7 - Check against the WHO guideline

Write `pct_exceeding_guideline(aq, guideline=15.0)`, returning the percentage (rounded to 1dp) of **non-missing** `pm2_5` readings that exceed the given guideline.
'''

PART7_TODO = '''
def pct_exceeding_guideline(aq, guideline=15.0):
    # TODO 11: percentage of non-null pm2_5 readings above `guideline`, rounded to 1dp.
    raise NotImplementedError("Complete this function, then delete this line.")


pct_exceeding = pct_exceeding_guideline(aq)
print(f"{pct_exceeding}% of readings exceed the WHO 24-hour guideline")
'''

PART7_SOLUTION = '''
def pct_exceeding_guideline(aq, guideline=15.0):
    valid = aq["pm2_5"].dropna()
    return round((valid > guideline).mean() * 100, 1)


pct_exceeding = pct_exceeding_guideline(aq)
print(f"{pct_exceeding}% of readings exceed the WHO 24-hour guideline")
'''

CHECK7 = '''
# Check cell. Must print True.
print("exceedance is the overwhelming majority:", pct_exceeding > 85)
'''

PART8_MD = '''
---
## Part 8 - Write the wrangling report

Write `wrangle_report`, a string. It must:

- state how many readings were missing and why that is plausible (sensor downtime, not explained by anything in the data itself);
- state how many stations and days the dataset covers;
- contain no code, column names, or library names;
- be roughly 150-400 words.
'''

PART8_TODO = '''
wrangle_report = """
# TODO 12: write your wrangling report here, following the structure above.
"""
'''

PART8_SOLUTION = '''
wrangle_report = """
This dataset covers daily air-quality readings from five sensors across Accra
for the whole of 2023 - 1,825 station-days in total.

Five of those station-days are missing a pollutant reading. In every case the
gap is a short run of consecutive days at a single station, consistent with a
sensor going offline rather than a data-entry problem - there is no missing
run longer than three days, and no station is missing more than three days
across the whole year. The weather measurements (temperature, humidity, wind
speed) are complete throughout, because they come from a separate source that
was not affected by the same outages.

No readings were removed and no values were estimated to fill the gaps; they
are left as missing, so that any yearly average correctly reflects slightly
fewer than 365 days for the three affected stations rather than silently
assuming a value for days nobody measured.

One caution for anyone building on this table: two multi-day spikes - one at
a single station, one affecting every station at once - sit inside the normal
range of dates and were not removed, because they are real, measured events,
not errors. Any yearly average calculated from this data already includes
them, which is appropriate for an annual summary but should be kept in mind
when comparing one week to another.
"""
'''

CHECK89 = '''
import re


def check_report(text, min_words, max_words, forbidden_substrings, required_keywords=None):
    words = len(text.split())
    has_forbidden = any(s in text for s in forbidden_substrings)
    has_required = all(k in text.lower() for k in (required_keywords or []))
    return {
        "word_count": words,
        "word_count_ok": min_words <= words <= max_words,
        "no_code_language": not has_forbidden,
        "required_keywords_present": has_required,
    }


wrangle_check = check_report(wrangle_report, 120, 450, ["_", "()", "df[", "import "])
print(wrangle_check)
'''

PART9_MD = '''
---
## Part 9 - Write the act report

Write `act_report`, a string, using the hook / ranked insights / so-what / limitations structure. It must:

- open with a one-sentence hook stating the overall WHO-guideline exceedance percentage from Part 7;
- include at least 3 ranked insights, each with at least one number (reuse your results from Parts 3-6);
- include a paragraph naming "so what" a reader should do;
- include a line naming at least one limitation;
- be roughly 150-350 words.
'''

PART9_TODO = '''
act_report = """
# TODO 13: write your act report here, following the structure above.
"""
'''

PART9_SOLUTION = '''
act_report = f"""
Every one of the five neighbourhoods in this study breathes air well outside
WHO guidance: {pct_exceeding}% of all station-days exceed the WHO 24-hour
PM2.5 guideline of 15 ug/m3.

Three patterns matter most. First, location is not a minor factor - the
worst-affected station type averages roughly {round(station_type_means.iloc[0] / station_type_means.iloc[-1], 1)}
times the PM2.5 of the cleanest one, and even the cleanest station type sits
above the guideline on most days. Second, the dry Harmattan season
(December-February) raises particulate matter by roughly
{effects['harmattan_pct_higher']:.0f}% over the rest of the year, citywide -
this is a predictable seasonal pattern, not a one-off. Third, nitrogen
dioxide - the pollutant most tied to traffic and generators - runs about
{effects['no2_weekday_pct_higher']:.0f}% higher on weekdays than weekends,
consistent with a traffic-linked source rather than a weather-linked one.

The data also contains one genuine citywide event, on {anomaly_dates[0]} and
{anomaly_dates[1]}, when every station - not just one - recorded several
times its normal reading. That rules out a single faulty sensor; whatever
happened affected the whole area at once.

So what: any air-quality response should prioritise the Harmattan months and
roadside locations first, since both push already-high levels substantially
higher, and should treat the two-day spike as a weather event worth
investigating on its own rather than folding into the yearly average.

Limitations: this covers one calendar year at five stations - it cannot say
whether 2023 was a typical year, and the five stations do not cover every
neighbourhood in Accra.
"""
'''

CHECK9 = '''
act_check = check_report(act_report, 120, 400, ["_(", "df[", "import "],
                          required_keywords=["so what", "limitation"])
numeric_claims = len(re.findall(r"\\d[\\d,]*\\.?\\d*", act_report))
print(act_check)
print("numeric claims:", numeric_claims, "(aim for at least 5)")
'''

PART10_MD = '''
---
## Part 10 - Save your deliverables

Write `save_reports(wrangle_report, act_report, output_dir)`, which writes `wrangle_report.md` and `act_report.md` into `output_dir` (creating it if needed) and returns a list of the two paths written.
'''

PART10_TODO = '''
def save_reports(wrangle_report, act_report, output_dir):
    # TODO 14: write both reports to output_dir / "wrangle_report.md" and "act_report.md".
    raise NotImplementedError("Complete this function, then delete this line.")


report_paths = save_reports(wrangle_report, act_report, Path("."))
print(report_paths)
'''

PART10_SOLUTION = '''
def save_reports(wrangle_report, act_report, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    wrangle_path = output_dir / "wrangle_report.md"
    act_path = output_dir / "act_report.md"
    wrangle_path.write_text(wrangle_report.strip() + "\\n")
    act_path.write_text(act_report.strip() + "\\n")
    return [wrangle_path, act_path]


report_paths = save_reports(wrangle_report, act_report, Path("."))
print(report_paths)
'''

CHECK10 = '''
# Check cell. Must print True.
print("both files written:", all(p.exists() for p in report_paths))
'''

PART11_MD = '''
---
### Your findings

**1. The one number you would lead with if you had thirty seconds with the council:**

*(Write your answer here.)*

**2. Which of the three multivariate effects (location, season, weekday) would you act on first, and why:**

*(Write your answer here.)*

**3. What you are least confident about in this dataset, and why:**

*(Write your answer here.)*
'''

RUBRIC_MD = '''
---
## Marking rubric

| Area | What earns the marks | Marks |
|---|---:|---:|
| Three questions (Part 2) | Specific, comparative, answerable; at least one comparison and one relationship question | 8 |
| First look and univariate (Parts 1, 3) | Correct shape, skew read correctly | 10 |
| Bivariate (Part 4) | Station-type ranking and wind correlation both correct | 10 |
| Multivariate (Part 5) | Both seasonal and weekday effects correct and real | 10 |
| Anomaly investigation (Part 6) | Both event dates found; correctly confirmed citywide, not single-station | 14 |
| WHO guideline check (Part 7) | Correct percentage, correctly described | 6 |
| Wrangling report (Part 8) | Passes its check; plain language; states what to trust and what not to | 16 |
| Act report (Part 9) | Passes its check; correct structure; numbers trace back to Parts 3-7; so-what is concrete | 18 |
| Saved deliverables (Part 10) | Both files written correctly | 4 |
| Findings | Numbers in every claim | 4 |
| Repository, structure, commits | Public repo, correct structure, useful commit messages | 10 |
| **Total** | | **110** |

Marks are lost for: a chart without a title stating a finding, a wrangling report containing any code or column name, an act report with fewer than 3 insights or no so-what, claiming a citywide pattern from evidence at one station, and `NotImplementedError` left anywhere.
'''

REFERENCES_MD = '''
## References

### Topic 22 material
- [Main lesson - Topic 22 Exploratory Data Analysis](../topic22_exploratory_data_analysis.ipynb)
- [22a - Asking good questions](../topic22a_asking_good_questions.ipynb)
- [22b - Univariate exploration](../topic22b_univariate_exploration.ipynb)
- [22c - Bivariate exploration](../topic22c_bivariate_exploration.ipynb)
- [22d - Multivariate exploration](../topic22d_multivariate_exploration.ipynb)
- [22e - From patterns to insights](../topic22e_patterns_to_insights.ipynb)
- [22f - Writing the wrangling report](../topic22f_writing_the_wrangling_report.ipynb)
- [22g - Writing the act report](../topic22g_writing_the_act_report.ipynb)

### Background
- [WHO global air quality guidelines (2021)](https://www.who.int/publications/i/item/9789240034228)
- [Cole Nussbaumer Knaflic, "Storytelling with Data"](https://www.storytellingwithdata.com/)

### Elsewhere in the course
- [Topic 20 - Data wrangling](../../data_wrangling/topic20_data_wrangling.ipynb)
- [Topic 21 - Data visualization](../../data_visualization/topic21_data_visualization.ipynb)
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
import matplotlib.pyplot as plt

PALETTE = {
    "blue": "#2a78d6", "aqua": "#1baf7a", "yellow": "#eda100", "green": "#008300",
    "violet": "#4a3aa7", "red": "#e34948", "magenta": "#e87ba4", "orange": "#eb6834",
}
MUTED = "#c3c2b7"
INK = "#0b0b0b"


def find_data_dir():
    candidates = [Path.cwd() / "data", Path.cwd() / "exploratory_data_analysis" / "data",
                  Path.cwd().parent / "data"]
    for candidate in candidates:
        if (candidate / "air_quality_readings_assignment.csv").exists():
            return candidate
    raise FileNotFoundError("Could not find air_quality_readings_assignment.csv. Looked in: " +
                             ", ".join(str(c) for c in candidates))


DATA_DIR = find_data_dir()
pd.set_option("display.max_columns", 30)
plt.rcParams["figure.dpi"] = 110
print("data folder:", DATA_DIR)
'''))

    cells.append(md(PART1_MD))
    cells.append(code(PART1_TODO))
    cells.append(code(CHECK1))

    cells.append(md(PART2_MD))
    cells.append(md(PART2_ANSWER_MD))

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

    cells.append(md(PART9_MD))
    cells.append(code(PART9_TODO))
    cells.append(code(CHECK89))
    cells.append(code(CHECK9))

    cells.append(md(PART10_MD))
    cells.append(code(PART10_TODO))
    cells.append(code(CHECK10))

    cells.append(md(PART11_MD))
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
    candidates = [Path.cwd() / "data", Path.cwd() / "exploratory_data_analysis" / "data",
                  Path.cwd().parent.parent / "exploratory_data_analysis" / "data"]
    for candidate in candidates:
        if (candidate / "air_quality_readings_assignment.csv").exists():
            return candidate
    raise FileNotFoundError("Could not find air_quality_readings_assignment.csv. Looked in: " +
                             ", ".join(str(c) for c in candidates))


DATA_DIR = find_data_dir()
pd.set_option("display.max_columns", 30)
plt.rcParams["figure.dpi"] = 110
print("data folder:", DATA_DIR)
'''))

    cells.append(md(PART1_MD))
    cells.append(code(PART1_SOLUTION))
    cells.append(code(CHECK1))

    cells.append(md(PART2_MD))
    cells.append(md('''
**Model questions:**

1. "How does mean PM2.5 differ between Roadside and Background stations?" (comparison)
2. "Is mean PM2.5 higher in Dec-Feb than the rest of the year, and by how much?" (trend/comparison)
3. "Does wind speed relate to PM2.5 in this new set of stations the same way it did in the lesson?" (relationship)
'''))

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

    cells.append(md(PART9_MD))
    cells.append(code(PART9_SOLUTION))
    cells.append(code(CHECK89))
    cells.append(code(CHECK9))

    cells.append(md(PART10_MD))
    cells.append(code(PART10_SOLUTION))
    cells.append(code(CHECK10))

    cells.append(md(PART11_MD.replace(
        "*(Write your answer here.)*",
        "*(Model answer - grade for numbers and reasoning, not exact wording.)*", 1)))
    cells.append(md('''
**Model answers:**

1. **Lead number:** 93.8% of all station-days in this sample exceed the WHO 24-hour PM2.5 guideline - this is not a tail-risk problem, it is the normal condition.
2. **Act on first:** location (Roadside vs. Background) - it is the largest and most consistent gap, and unlike the Harmattan season, it is something infrastructure and zoning decisions can actually change.
3. **Least confident about:** one calendar year at five stations cannot distinguish a genuine trend from normal year-to-year variation, and five stations do not represent every part of Accra - particularly, there is no second Background site to confirm Legon is typical of "clean" areas generally.
'''))
    cells.append(md(RUBRIC_MD))
    cells.append(md(REFERENCES_MD))
    return nb(cells)


if __name__ == "__main__":
    write(build_assignment(), HERE / "assignments" / "topic22_assignment_air_quality_eda.ipynb")
    write(build_solutions(), HERE.parent / "instructor_solutions" / "exploratory_data_analysis" /
          "topic22_assignment_air_quality_eda_solutions.ipynb")
