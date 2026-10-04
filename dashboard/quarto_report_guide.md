# Quarto Report Guide

The report source is [`../reports/sales_report.qmd`](../reports/sales_report.qmd). It uses Python code cells to read the project's CSV, calculate metrics, and build charts and tables in one reproducible HTML report.

## Prerequisites

- Python 3.10 or later
- Quarto CLI
- The Python packages listed in `requirements.txt`, including `ipykernel`

Install Quarto from [quarto.org](https://quarto.org/docs/get-started/). Then, from the repository root, install the Python dependencies into the environment you plan to use for rendering:

```powershell
python -m pip install -r requirements.txt
```

The requirements file includes the Jupyter components Quarto needs to execute Python cells (`jupyter`, `jupyter_client`, `nbformat`, `nbclient`, `ipykernel`, and `traitlets`). Install them in the same Python environment Quarto will use. For a global Python 3.11 install instead of a virtual environment, the equivalent command is:

```powershell
py -3.11 -m pip install jupyter jupyter_client nbformat nbclient ipykernel traitlets
```

## Render and preview

```powershell
quarto render reports/sales_report.qmd
```

This creates `reports/sales_report.html`. To preview edits and rerender automatically:

```powershell
quarto preview reports/sales_report.qmd
```

Run Quarto from the activated Python environment so its Jupyter engine can find the `python3` kernel. The report reads `data/sales_data.csv`; it does not require the SQLite database to exist.

## Modify the report

Edit the Markdown sections for narrative and the `{python}` cells for analysis, tables, and charts. Since calculations run during rendering, the report reflects the current CSV contents. The report currently includes KPIs, monthly and annual revenue, category and product results, regional performance, and a channel comparison.

HTML is the default output and does not require a PDF toolchain. PDF rendering requires a LaTeX installation such as TinyTeX; install that only if PDF output is needed.
