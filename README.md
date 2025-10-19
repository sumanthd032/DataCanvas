# DataCanvas: Smart SQLite Visualizer & Analyzer

DataCanvas is a Streamlit app that lets you upload an SQLite database, explore its schema, run custom SQL, and auto-generate profiles, visualizations, and plain‑English insights.

![DataCanvas](https://placehold.co/800x300/F0F2F6/4F8BF9?text=Upload+a+Database+to+Begin&font=inter)

## Features

- Database upload: drag-and-drop any .sqlite or .db file
- Schema explorer: list tables and preview first rows
- Custom SQL runner: safely execute ad‑hoc queries and view results
- Automated profiling: row/column counts, missing values, numeric stats
- Smart visualizations:
	- Univariate: histograms (numeric), bar charts (categorical)
	- Bivariate: correlation heatmap, box plots (numeric vs. categorical)
- Automated insights: highlights strong correlations, missing data, and high-cardinality columns

## Tech stack

- Frontend: Streamlit
- Data: pandas, NumPy
- DB: SQLite3 (built into Python)
- Viz: Matplotlib, Seaborn

## Prerequisites

- Python 3.8+ recommended

## Setup

1) Create and activate a virtual environment

macOS/Linux (zsh/bash):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

## Run

Start the Streamlit app from the project root:

```bash
streamlit run app.py
```

Your browser should open automatically. If not, visit the URL shown in the terminal (typically http://localhost:8501).

## How to use

1) Upload an SQLite file (.sqlite or .db) from the sidebar
2) Pick a table to preview rows and explore
3) Use the tabs to:
	 - Data Profile: see table-level stats and missing values
	 - Single Column Analysis: histogram/bar chart per column
	 - Bivariate Analysis: correlation heatmap and box plots
	 - Automated Insights: plain‑English highlights
4) Optional: open “Run a Custom SQL Query” to execute your own SQL

## Project structure

```
.
├── app.py            # Streamlit app entry point
├── README.md         # You are here
├── requirements.txt  # Python dependencies
└── temp_data/        # Temporary storage for uploaded DBs
```

## Troubleshooting

- Empty or no tables: ensure your uploaded DB has tables; views aren’t listed
- Not enough numeric/categorical columns: some charts require specific types
- Matplotlib/Seaborn backend errors: ensure the venv is active and deps installed

## Notes

- SQLite3 is part of the Python standard library—no extra install required
- Large databases may take longer to load and visualize