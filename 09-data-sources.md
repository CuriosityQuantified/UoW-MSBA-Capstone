# 09-data-sources.md — Full Content

# 09 — Data Sources for AI & Data Science Projects

A curated reference of high-quality, free or low-cost data sources suitable for capstone projects, research, and production AI systems. Organized by domain.

---

## Quick Navigation

- [General / Starting Points](#general--starting-points)
- [Government & Open Data](#government--open-data)
- [Financial & Economic](#financial--economic)
- [Healthcare & Life Sciences](#healthcare--life-sciences)
- [NLP, Text & LLM Corpora](#nlp-text--llm-corpora)
- [Academic & Social Science Repositories](#academic--social-science-repositories)

---

## General / Starting Points

| Source | URL | What It Has | Access |
|--------|-----|-------------|--------|
| **Kaggle Datasets** | kaggle.com/datasets | 50K+ community datasets across all domains; labeled, clean, notebook-ready | Free account; `pip install kaggle` |
| **Hugging Face Datasets** | huggingface.co/datasets | 500K+ ML-ready datasets (NLP, vision, tabular, multimodal) | `pip install datasets` → `load_dataset("name")` |
| **data.world** | data.world | Social/civic datasets; collaborative data platform | Free tier; REST API + Python SDK |
| **Google Dataset Search** | datasetsearch.research.google.com | Meta-search across thousands of dataset repositories | Web only |
| **AWS Open Data Registry** | registry.opendata.aws | Large-scale datasets hosted free on S3 (genomics, satellite, weather, NLP) | `aws s3 cp` or boto3; no egress fees in us-east-1 |

---

## Government & Open Data

| # | Source | URL | Data Types | Programmatic Access | License |
|---|--------|-----|-----------|---------------------|---------|
| 1 | **data.gov (US)** | data.gov | 280K+ datasets: health, climate, agriculture, education, finance, geospatial | CKAN API (`catalog.data.gov/api/3`); Socrata API (`sodapy`) | Public domain (federal); varies for state/local |
| 2 | **US Census Bureau** | data.census.gov | Demographics, housing, ACS, Decennial Census, economic surveys | Free API key at census.gov/developers; `pip install census` | Public domain |
| 3 | **World Bank Open Data** | data.worldbank.org | 1,400+ global development indicators across 200+ economies, back to 1960 | `pip install wbgapi`; no key needed | CC BY 4.0 |
| 4 | **FRED (St. Louis Fed)** | fred.stlouisfed.org | 800K+ US/global macro series: GDP, CPI, unemployment, interest rates, housing | Free API key; `pip install fredapi` | Public domain |
| 5 | **Eurostat** | ec.europa.eu/eurostat | EU member state statistics: economics, demographics, health, energy, trade | `pip install eurostat`; SDMX-JSON API (no key) | CC BY 4.0 |
| 6 | **EU Open Data Portal** | data.europa.eu | 1M+ EU institutional datasets; 24 languages | CKAN API + SPARQL endpoint | CC BY 4.0 |
| 7 | **OECD Stats** | stats.oecd.org | GDP, employment, PISA, health, environment across 38 OECD members | SDMX-JSON API (no key); `pandas-datareader` | CC BY 4.0 |
| 8 | **UN Data** | data.un.org | Global stats from all UN agencies: population, trade, energy, environment | SDMX API; `undata-api.org` (free key) | Free non-commercial; attribution required |
| 9 | **IMF Data** | data.imf.org | Balance of payments, IFS, WEO projections, debt sustainability — 190+ countries | `pip install imfp`; SDMX-JSON API (no key) | Free research/education use |
| 10 | **BIS Data Portal** | data.bis.org | Global banking stats, forex turnover, OTC derivatives, property prices | SDMX REST API (no key); CSV direct download | Free with attribution |
| 11 | **NOAA Climate Data Online** | ncdc.noaa.gov/cdo-web | Historical weather, precipitation, storms, ocean data — global stations | Free API token; `pip install noaa-sdk`; open-meteo.com (no key) | Public domain |
| 12 | **FBI Crime Data Explorer** | cde.ucr.cjis.gov | UCR crimes, NIBRS incident data, hate crimes, arrests — US national | Free API key; bulk CSV download | Public domain |
| 13 | **HealthData.gov** | healthdata.gov | HHS datasets: hospital quality, EHR adoption, insurance coverage | DKAN API; direct CSV/JSON | Public domain |
| 14 | **Open Government Canada** | open.canada.ca | Geospatial, economic, environmental, bilingual (EN/FR) federal data | CKAN API | Open Government License – Canada |
| 15 | **data.gov.au** | data.gov.au | Australian government: environment, agriculture, infrastructure, demographics | CKAN API | CC BY 4.0 |

**Best for capstone projects:**
- Easiest Python access: World Bank (`wbgapi`) and Eurostat (`eurostat`) — 2-line DataFrame pulls
- Broadest US coverage: data.gov (280K datasets)
- Best macro time-series: FRED (public domain, extremely clean)
- Best for climate/weather ML: NOAA + open-meteo.com

---

## Financial & Economic

| # | Source | URL | Cost | Programmatic Access | Notes |
|---|--------|-----|------|---------------------|-------|
| 1 | **Yahoo Finance** | finance.yahoo.com | Free (unofficial) | `pip install yfinance` | OHLCV, financials, options, crypto; not licensed for commercial redistribution |
| 2 | **FRED** | fred.stlouisfed.org | Free | `pip install fredapi` (free key) | See Government section; public domain |
| 3 | **Alpha Vantage** | alphavantage.co | Free tier (25 req/day) | `pip install alpha-vantage` | Equities, forex, crypto, 50+ technical indicators, news sentiment |
| 4 | **Nasdaq Data Link** | data.nasdaq.com | Free + paid tiers | `pip install nasdaq-data-link` | 250+ databases; WIKI EOD prices, Zillow housing, ODA macro (free); Sharadar fundamentals (paid) |
| 5 | **SEC EDGAR** | data.sec.gov | Free, no auth | `pip install edgartools`; REST API | All 10-K/10-Q/8-K filings since 1993; XBRL machine-readable financials; public domain |
| 6 | **IMF Data** | data.imf.org | Free | `pip install imfp` | See Government section |
| 7 | **BIS Data Portal** | data.bis.org | Free | SDMX REST API | See Government section |
| 8 | **World Bank** | data.worldbank.org | Free | `pip install wbgapi` | See Government section |
| 9 | **OECD Data** | data.oecd.org | Free | SDMX-JSON API | See Government section |
| 10 | **OpenBB Platform** | openbb.co | Free/open-source | `pip install openbb` | Unified wrapper over yfinance, Alpha Vantage, FRED, Polygon, ECB, and more |
| 11 | **Polygon.io** | polygon.io | Free tier (5 req/min) | Official Python client + REST API | Exchange-grade US equities, options, crypto; paid from $29/mo for real-time |
| 12 | **WRDS** | wrds-www.wharton.upenn.edu | Free via university | Python JupyterHub via institution | CRSP + Compustat + OptionMetrics + TAQ — academic gold standard; institutional access required |
| 13 | **CMS Medicare SynPUF** | cms.gov | Free, no auth | Direct CSV download | Synthetic Medicare claims (Parts A/B/D); ~2.3M synthetic patients; no DUA required |

**Quick decision matrix:**

| Use Case | Best Source(s) |
|----------|---------------|
| Stock price prediction / LSTM | yfinance, Alpha Vantage, Polygon.io |
| Macro forecasting | FRED, World Bank, IMF, OECD |
| NLP on SEC filings / earnings calls | SEC EDGAR (edgartools) |
| Quant research / factor models | WRDS (CRSP+Compustat), Nasdaq Data Link (Sharadar) |
| Credit / fraud detection | Kaggle labeled datasets, FRED |
| Global / systemic risk | BIS, IMF, World Bank |
| Multi-source aggregation | OpenBB Platform |

---

## Healthcare & Life Sciences

| # | Source | URL | Access Tier | Programmatic Access |
|---|--------|-----|-------------|---------------------|
| 1 | **MIMIC-IV** | physionet.org/content/mimiciv | Free, credentialed (CITI training + DUA, ~2 weeks) | Direct download; BigQuery; `mimic-code` tools |
| 2 | **MIMIC-IV Demo** | physionet.org/content/mimic-iv-demo | Fully open — no registration | Direct download; AWS Open Data |
| 3 | **eICU CRD** | physionet.org/content/eicu-crd | Free, credentialed (same as MIMIC) | Direct download; BigQuery |
| 4 | **NHANES** | cdc.gov/nchs/nhanes | Fully open | `pandas.read_sas()`; `pip install nhanes-dl` |
| 5 | **CDC Open Data** | data.cdc.gov | Fully open | Socrata API (`sodapy`); no key required |
| 6 | **CMS data.cms.gov** | data.cms.gov | Fully open (aggregate); DUA for patient-level | REST API; CSV bulk download |
| 7 | **CMS Medicare SynPUF** | cms.gov | Fully open — no registration | Direct CSV download |
| 8 | **OpenFDA** | open.fda.gov | Fully open | REST API; `pip install python-openfda`; 1K req/day free, 120K/day with free key |
| 9 | **ClinicalTrials.gov API v2** | clinicaltrials.gov/data-api | Fully open | REST API v2 (2024); AACT PostgreSQL mirror (`aact-db.ctti-clinicaltrials.org`) |
| 10 | **TCGA via GDC Portal** | cancer.gov/ccg/research/genome-sequencing/tcga | Open-tier free; controlled-access via dbGaP | `pip install gdc-client`; GDC REST API |
| 11 | **TCIA (Cancer Imaging Archive)** | cancerimagingarchive.net | Most open after free account | `pip install tcia-utils`; TCIA REST API |
| 12 | **NIH Chest X-ray Dataset** | kaggle.com/datasets/nih-chest-xrays | Fully open via Kaggle | `kaggle datasets download nih-chest-xrays/data` |
| 13 | **SEER** | seer.cancer.gov | Free, requires account + software agreement | SEER*Stat desktop; bulk text file download |
| 14 | **NIH dbGaP** | ncbi.nlm.nih.gov/gap | Open summaries; controlled-access individual data | `dbGaP-downloader`; SRA Toolkit |
| 15 | **Human Connectome Project** | humanconnectome.org | Free account required | Aspera/S3 download; `hcp-utils` Python package |
| 16 | **UK Biobank** | ukbiobank.ac.uk | Institutional affiliation required; fee ~£2K–£10K+ | `ukbb_parser`; bulk download tool |
| 17 | **PhysioNet (general)** | physionet.org | Mix of open and credentialed | `pip install wfdb`; FTP direct download |
| 18 | **HealthData.gov** | healthdata.gov | Fully open | DKAN API; CSV/JSON direct download |

**Access tier summary:**

| Tier | Sources |
|------|---------|
| Zero friction (no registration) | NHANES, CDC Open Data, CMS SynPUF, OpenFDA, ClinicalTrials.gov, NIH Chest X-ray, HealthData.gov |
| Free with account/DUA (days–weeks) | MIMIC-IV, eICU, TCIA (most), SEER, GDC open-tier |
| Controlled-access (institutional + formal application) | NIH dbGaP individual data, UK Biobank (fee-based) |

**Bottom line:** Start with NHANES + OpenFDA + ClinicalTrials.gov for zero-friction projects. MIMIC-IV Demo unlocks EHR work immediately. Full MIMIC-IV requires ~2 weeks for CITI + DUA but is worth it for serious clinical ML. TCGA/TCIA for cancer imaging and genomics.

---

## NLP, Text & LLM Corpora

### Pretraining Corpora

| # | Name | Size | License | Access |
|---|------|------|---------|--------|
| 1 | **Common Crawl** | 300B+ pages (~100TB raw) | Open (CC Terms of Use) | `aws s3 cp s3://commoncrawl/` |
| 2 | **FineWeb** | 15T tokens | ODC-BY | `load_dataset("HuggingFaceFW/fineweb", name="sample-10BT", streaming=True)` |
| 3 | **FineWeb-Edu** | ~1.3T tokens | ODC-BY | `load_dataset("HuggingFaceFW/fineweb-edu", name="sample-10BT")` |
| 4 | **C4** | ~156B tokens | ODC-BY | `load_dataset("allenai/c4", "en")` |
| 5 | **The Pile (EleutherAI)** | 825 GiB, 22 subsets | Mixed (MIT + CC) | `load_dataset("monology/pile-uncopyrighted")` (safe subset) |
| 6 | **Common Pile v0.1** | ~8TB | Public domain / open only | `load_dataset("EleutherAI/common-pile")` |
| 7 | **RedPajama-Data-1T** | 1T tokens | Apache 2.0 | `load_dataset("togethercomputer/RedPajama-Data-1T")` |
| 8 | **RedPajama-Data-V2** | 30T tokens (with quality signals) | Apache 2.0 | `load_dataset("togethercomputer/RedPajama-Data-V2", name="sample")` |
| 9 | **Dolma (AllenAI)** | ~3T tokens | ODC-BY | `load_dataset("allenai/dolma", streaming=True)` |
| 10 | **OSCAR (Multilingual)** | 6.3TB+ | CC0 (ethics charter required) | `load_dataset("oscar-corpus/OSCAR-2301", lang)` |
| 11 | **OpenWebText** | ~40GB / ~8M docs | CC0 | `load_dataset("Skylion007/openwebtext")` |
| 12 | **Wikipedia (HF)** | ~20GB/lang | CC-BY-SA 4.0 | `load_dataset("wikimedia/wikipedia", "20231101.en")` |
| 13 | **The Stack v2 (BigCode)** | ~900B tokens | Various (opt-out) | `load_dataset("bigcode/the-stack-v2", streaming=True)` |

**Which to use:**
- **Best overall pretraining (2024–2025):** FineWeb or FineWeb-Edu — better quality signals than C4
- **Legally safest:** Common Pile v0.1 (public domain + permissive only)
- **Multilingual:** OSCAR-2301 (150+ languages)
- **Code:** The Stack v2
- **RAG / factual grounding:** Wikipedia (HF)

### Instruction Tuning & Alignment Datasets

| # | Name | Size | License | Access |
|---|------|------|---------|--------|
| 14 | **Stanford Alpaca** | 52K examples | CC BY-NC 4.0 ⚠️ | `load_dataset("tatsu-lab/alpaca")` |
| 15 | **OpenHermes 2.5** | ~1M GPT-4 examples | Apache 2.0 | `load_dataset("teknium/OpenHermes-2.5")` |
| 16 | **OpenOrca** | 4.2M FLAN-augmented | MIT | `load_dataset("Open-Orca/OpenOrca")` |
| 17 | **FLAN Collection** | 1,836 NLP tasks | Apache 2.0 | `load_dataset("Open-Orca/FLAN")` |
| 18 | **UltraFeedback** | 64K prompts × 4 responses | MIT | `load_dataset("openbmb/UltraFeedback")` |
| 19 | **Anthropic HH-RLHF** | ~169K preference pairs | MIT | `load_dataset("Anthropic/hh-rlhf")` |

⚠️ Stanford Alpaca is non-commercial only (CC BY-NC 4.0). For commercial fine-tuning use OpenHermes 2.5 or OpenOrca.

---

## Academic & Social Science Repositories

| # | Source | URL | Data Types | Programmatic Access | License |
|---|--------|-----|-----------|---------------------|---------|
| 1 | **UCI ML Repository** | archive.ics.uci.edu | 689+ curated ML datasets (tabular, time series, text) | `pip install ucimlrepo`; `from ucimlrepo import fetch_ucirepo` | CC BY 4.0 (per dataset) |
| 2 | **OpenML** | openml.org | Thousands of datasets; benchmark suites (CC18, OpenML-100) | `pip install openml`; REST API; sklearn integration | CC0 / CC BY (per dataset) |
| 3 | **Stanford SNAP** | snap.stanford.edu/data | 50+ large graph datasets: social networks, citation, Reddit, Amazon | Direct download (`.txt.gz`); `snap.py` Python library | Custom open (academic use; citation required) |
| 4 | **GDELT Project** | gdeltproject.org | Global news events + sentiment; 15-min updates since 1979; 100+ languages | `pip install gdelt`; Google BigQuery (free tier); CSV direct | Open / free |
| 5 | **Harvard Dataverse** | dataverse.harvard.edu | 75,000+ research datasets: political science, sociology, economics, health | `pip install pyDataverse`; REST API with DOI lookup | CC0 (default); varies per depositor |
| 6 | **Zenodo** | zenodo.org | All research outputs: datasets, software, preprints — all domains | REST API (`zenodo.org/api/records`); `pip install zenodopy` | CC BY 4.0 (default); varies |
| 7 | **ICPSR** | icpsr.umich.edu | 9,000+ social science surveys: political behavior, crime, health, education | Web download (free account); `icpsrdata` R package | Free with registration; some require institutional membership |
| 8 | **Pew Research Datasets** | pewresearch.org/datasets | American Trends Panel; political, religious, technology surveys | Direct download (SPSS/CSV) after free registration | Free non-commercial; attribution required |
| 9 | **General Social Survey (GSS)** | gss.norc.org | Annual US household survey 1972–2024; 6,000+ variables | Direct download (SPSS/Stata); GSS Data Explorer; Kaggle mirror (CSV) | Free for research; NORC attribution required |
| 10 | **World Values Survey** | worldvaluessurvey.org | Cross-national values surveys; 100+ countries, 7 waves (1981–2022) | Direct download (SPSS/CSV) after free registration | CC BY-NC (academic use free) |
| 11 | **PhysioNet** | physionet.org | ECG, EEG, waveforms, MIMIC clinical data, sleep studies | `pip install wfdb`; REST API; credentialed for sensitive data | ODC-BY (open); credentialed for MIMIC |

---

## Quick Picks by Use Case

| Use Case | Recommended Sources |
|----------|-------------------|
| **Tabular ML / classification baseline** | UCI ML Repo, OpenML, Kaggle |
| **Graph neural networks** | Stanford SNAP |
| **NLP pretraining (English)** | FineWeb, Dolma, C4 |
| **LLM fine-tuning / instruction** | OpenHermes 2.5, OpenOrca, FLAN Collection |
| **RLHF / alignment** | Anthropic HH-RLHF, UltraFeedback |
| **Code generation** | The Stack v2 |
| **Stock price / quant finance** | yfinance, FRED, Alpha Vantage, SEC EDGAR |
| **Macro economics** | FRED, World Bank, IMF, OECD |
| **Clinical / EHR** | MIMIC-IV (credentialed), NHANES (open), CMS SynPUF (open) |
| **Medical imaging** | TCGA, TCIA, NIH Chest X-ray |
| **Public health / epidemiology** | CDC Open Data, OpenFDA, ClinicalTrials.gov |
| **Social science / surveys** | GSS, World Values Survey, Pew, ICPSR |
| **Geopolitical / news NLP** | GDELT (BigQuery) |
| **Reproducibility / published papers** | Zenodo, Harvard Dataverse |
| **Government / civic data** | data.gov, Census API, EU Open Data Portal |
