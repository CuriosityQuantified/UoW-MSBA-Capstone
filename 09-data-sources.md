# 09 — Data Sources

> Good agents need good data. This section catalogs high-quality, free or low-cost data sources suitable for capstone projects — structured datasets, time series, NLP corpora, financial data, and more.

---

## Core Sources

### 🤗 Hugging Face Datasets
**URL:** <https://huggingface.co/datasets>
**Best for:** NLP, LLM fine-tuning, benchmarks, multimodal
**Highlights:**
- 100K+ datasets across NLP, vision, audio, tabular
- Loads directly into Python via `datasets` library (`load_dataset("name")`)
- Includes many LLM-specific sets: instruction tuning, RLHF preference data, evals
- Search by task, language, license, size

```python
from datasets import load_dataset
ds = load_dataset("imdb")
```

---

### 📊 Kaggle Datasets
**URL:** <https://www.kaggle.com/datasets>
**Best for:** Tabular ML, competitions, domain-specific structured data
**Highlights:**
- 300K+ datasets; most are free under open licenses
- Strong in: healthcare, finance, sports, retail, NLP
- Notebooks attached to most datasets — see how others approached the problem
- API access: `kaggle datasets download -d <owner/dataset>`

```bash
pip install kaggle
kaggle datasets download -d uciml/iris
```

---

### 🌐 data.world
**URL:** <https://data.world>
**Best for:** Social good, government, journalism, cross-dataset joins
**Highlights:**
- Collaborative platform — datasets with context, provenance, and linked queries
- Strong civic/policy datasets: elections, education, health equity
- SQL-queryable directly in browser
- Free tier available; academic access through institutional licenses

---

### 🏦 FRED — Federal Reserve Bank of St. Louis
**URL:** <https://fred.stlouisfed.org>
**Best for:** Economic indicators, monetary policy, financial time series
**Highlights:**
- 800K+ time series from 100+ sources (BLS, BEA, Census, Fed, World Bank)
- Free API with generous rate limits
- Python: `fredapi` library
- Key series: GDP, CPI, unemployment, interest rates, M2, housing starts

```python
from fredapi import Fred
fred = Fred(api_key="YOUR_API_KEY")  # Free at fred.stlouisfed.org/docs/api/
gdp = fred.get_series("GDP")
```

---

## Additional High-Quality Sources

*Expanded via research swarm — see below for updates.*

---

## By Use Case

| Use Case | Recommended Sources |
|----------|-------------------|
| NLP / LLM training | Hugging Face, Common Crawl, The Pile |
| Financial modeling | FRED, Quandl/Nasdaq Data Link, Yahoo Finance |
| Healthcare | CMS, MIMIC-III (PhysioNet), CDC Open Data |
| Government / policy | data.gov, data.world, OECD Stats |
| Retail / e-commerce | Kaggle, UC Irvine ML Repository |
| Social / behavioral | ICPSR, Pew Research, GDELT |
| Geospatial | OpenStreetMap, NASA Earthdata, NOAA |
| Computer vision | Hugging Face, Roboflow Universe, ImageNet |

---

## Tips for Capstone Projects

1. **Check the license first** — CC BY, CC0, and ODC-OBL are permissive; avoid NC (non-commercial) restrictions if you're presenting publicly
2. **Prefer programmatic access** — datasets with APIs or Python library integrations save hours of manual download/clean cycles
3. **Look for data cards** — Hugging Face and Kaggle include metadata on collection method, known biases, and intended use; read them before building on a dataset
4. **Version your data** — store a local snapshot with a download timestamp; APIs change and datasets get updated
5. **Small ≠ bad** — a 10K-row clean dataset is often better for agent development than a 10M-row noisy one; agents amplify data quality issues
