# chrono_EF
Chronosequence modeling for emission factor of seagrass ecosystem carbon inventory

## Chronosequence-based Seagrass Carbon Emission Factors (Indonesia)

Code by: A'an J. Wahyudi (Dec 1, 2025); the code is generated using the assistance of OpenAI GPT 5.1 and curated by the author.
This repository contains a modular workflow to compute **carbon emission factors (EF)**
for seagrass ecosystems using **chronosequence modelling** and the
**Seagrass Ecological Quality Index (SEQI)**.

The workflow is designed to be reproducible in **Python** and easily portable to
**Google Colab**.


---

## Folder structure

- `01_load_clean.py` – load Excel template, QA/QC, compute total carbon stocks
- `02_seqi_model.py` – define effective SEQI (`SEQI_star`; hook for imputation)
- `03_chronosequence_EF.py` – compute `EF_stock` and `EF_chrono`
- `04_mapping.py` – quick map of `EF_chrono` across sites
- `00_requirements.txt` – list of required Python packages
- `sample/Seagrass_Carbon_for_EF_Dataset_Template.xlsx` – example template (optional)

---

## Input template

The code expects an Excel file with the following columns:

- `Date`
- `Location`
- `Site`
- `Latitude`
- `Longitude`
- `Convertion Activity Cluster`
- `Convertion Activities`
- `Years Since Convertion`
- `Dominant Species`
- `SEQI`
- `Carbon AGC (g C/m²)`
- `Carbon BGC (g C/m²)`
- `Carbon Soil (g C/m²)`
- `Soil Depth (cm)`
- (other ecological descriptors are preserved but not required for EF)

---

## Running the workflow

### 1. Install dependencies

```bash
pip install -r 00_requirements.txt
```
### 2. Load and clean dataset
```bash
python 01_load_clean.py \
  --input sample/Seagrass_Carbon_for_EF_Dataset_Template.xlsx \
  --output work/cleaned.xlsx
```
### 3. SEQI modeling
```bash
python 02_seqi_model.py \
  --input work/cleaned.xlsx \
  --output work/cleaned_seqi.xlsx
```
### 4. Chronosequence EF calculation
```bash
python 03_chronosequence_EF.py \
  --input work/cleaned_seqi.xlsx \
  --output work/EF_results.xlsx \
  --cref_global 13
```

### Optional: mapping
```bash
python 04_mapping.py \
  --input work/EF_results.xlsx \
  --output figures/EF_chrono_map.png
```

## Google Colab usage

In Colab:

Mount Google Drive.

Clone this repository into /content.

Run the scripts from code cells using !python ... commands,
pointing to your file paths inside Drive.
