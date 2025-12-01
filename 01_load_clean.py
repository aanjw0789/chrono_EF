"""
01_load_clean.py

Load the seagrass EF template, perform basic QA/QC, and compute
total carbon stocks (AGC + BGC + soil) in g C m^-2 and t C ha^-1.
"""

import pandas as pd
import numpy as np
from pathlib import Path


# Exact column names as in the template
COL_DATE = "Date"
COL_LOCATION = "Location"
COL_SITE = "Site"
COL_LAT = "Latitude"
COL_LON = "Longitude"
COL_CLUSTER = "Convertion Activity Cluster"
COL_ACTIVITIES = "Convertion Activities"
COL_T_YEARS = "Years Since Convertion"
COL_DOM_SPECIES = "Dominant Species"
COL_SEQI = "SEQI"
COL_AGC = "Carbon AGC \n(g C/m²)"
COL_BGC = "Carbon BGC \n(g C/m²)"
COL_SOIL = "Carbon Soil \n(g C/m²)"
COL_SOIL_DEPTH = "Soil Depth (cm)"


def load_and_clean(input_path: str) -> pd.DataFrame:
    """
    Load the EF template Excel file and compute total carbon stocks.

    Parameters
    ----------
    input_path : str
        Path to the Excel file.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame with additional columns:
        - C_tot_g_m2
        - C_tot_tC_ha
        - t_obs
    """
    input_path = Path(input_path)
    df = pd.read_excel(input_path)

    # Basic presence check of key columns
    needed = [
        COL_LOCATION, COL_SITE, COL_LAT, COL_LON,
        COL_CLUSTER, COL_T_YEARS, COL_SEQI,
        COL_AGC, COL_BGC, COL_SOIL
    ]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in dataset: {missing}")

    # Convert numeric columns safely
    num_cols = [COL_LAT, COL_LON, COL_T_YEARS,
                COL_SEQI, COL_AGC, COL_BGC, COL_SOIL, COL_SOIL_DEPTH]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Total carbon in g C m^-2
    df["C_tot_g_m2"] = (
        df[COL_AGC].fillna(0.0)
        + df[COL_BGC].fillna(0.0)
        + df[COL_SOIL].fillna(0.0)
    )

    # Convert to t C ha^-1: 1 g m^-2 = 0.01 t ha^-1
    df["C_tot_tC_ha"] = df["C_tot_g_m2"] * 0.01

    # Observed time since conversion
    df["t_obs"] = pd.to_numeric(df[COL_T_YEARS], errors="coerce")

    return df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Load EF dataset and compute total carbon stocks."
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to template Excel file"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to save cleaned CSV/Excel (extension determines format)"
    )

    args = parser.parse_args()

    df = load_and_clean(args.input)
    out_path = Path(args.output)

    if out_path.suffix.lower() in [".xlsx", ".xlsm"]:
        df.to_excel(out_path, index=False)
    else:
        df.to_csv(out_path, index=False)

    print(f"Saved cleaned dataset with carbon stocks to: {out_path}")
