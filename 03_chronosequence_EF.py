"""
03_chronosequence_EF.py

Compute carbon emission factors using:
- stock-difference EF
- chronosequence + SEQI-based EF

Requires a dataset that already contains:
- C_tot_tC_ha
- t_obs
- SEQI_star
- Convertion Activity Cluster
"""

import numpy as np
import pandas as pd
from pathlib import Path

from 01_load_clean import (
    COL_CLUSTER,
    COL_SEQI,
)
SEQI_REF_THRESHOLD = 0.80   # reference condition
R_DECAY = 0.028              # 2.8 % per year


def compute_efs(df: pd.DataFrame,
                cref_global: float = 13.0) -> pd.DataFrame:
    """
    Add EF_stock and EF_chrono columns to the DataFrame.

    Parameters
    ----------
    df : DataFrame
        Input data with columns: C_tot_tC_ha, t_obs, SEQI_star, cluster.

    cref_global : float
        Fallback global baseline if a cluster has no reference sites.

    Returns
    -------
    df_out : DataFrame
        Copy of df with new EF-related columns.
    """
    df = df.copy()

    # ------------------------------------------------------------------
    # 1. Site types: Reference vs Disturbed
    # ------------------------------------------------------------------
    seqi_star = df.get("SEQI_star", df[COL_SEQI])
    df["SEQI_star"] = seqi_star

    # Observed time since conversion
    df["t_obs_clean"] = df["t_obs"].where(df["t_obs"] > 0, np.nan)

    ref_mask = (df["SEQI_star"] >= SEQI_REF_THRESHOLD) & (
        df["t_obs_clean"].isna()
    )
    dist_mask = df["t_obs_clean"] > 0

    df["Site_Type"] = np.where(ref_mask, "Reference",
                               np.where(dist_mask, "Disturbed", "Undefined"))

    # ------------------------------------------------------------------
    # 2. Baseline carbon per cluster
    # ------------------------------------------------------------------
    ref_df = df.loc[ref_mask & df["C_tot_tC_ha"].notna(),
                    [COL_CLUSTER, "C_tot_tC_ha"]]

    Cref_group = ref_df.groupby(COL_CLUSTER)["C_tot_tC_ha"].median()
    df["C_ref_group"] = df[COL_CLUSTER].map(Cref_group)
    df["C_ref_group"] = df["C_ref_group"].fillna(cref_global)

    # ------------------------------------------------------------------
    # 3. Optional: derive time from SEQI (linear)
    # ------------------------------------------------------------------
    df["t_from_SEQI_lin"] = np.where(
        (df["SEQI_star"].notna())
        & (df["SEQI_star"] < SEQI_REF_THRESHOLD)
        & (R_DECAY > 0),
        (SEQI_REF_THRESHOLD - df["SEQI_star"]) / R_DECAY,
        np.nan,
    )

    # Priority: observed t, then SEQI-based t
    df["t_used"] = df["t_obs_clean"].fillna(df["t_from_SEQI_lin"])

    # ------------------------------------------------------------------
    # 4. Stock-difference EF
    # ------------------------------------------------------------------
    df["deltaC_stock"] = df["C_ref_group"] - df["C_tot_tC_ha"]
    df.loc[df["deltaC_stock"] < 0, "deltaC_stock"] = 0

    df["EF_stock"] = df["deltaC_stock"] / df["t_used"]
    df.loc[~dist_mask, "EF_stock"] = np.nan

    # ------------------------------------------------------------------
    # 5. Chronosequence + SEQI EF
    # ------------------------------------------------------------------
    df["deltaC_chrono"] = df["C_ref_group"] * (
        1 - (df["SEQI_star"] / SEQI_REF_THRESHOLD)
    )
    df.loc[df["SEQI_star"] >= SEQI_REF_THRESHOLD, "deltaC_chrono"] = 0

    df["EF_chrono"] = df["deltaC_chrono"] / df["t_used"]
    df.loc[~dist_mask, "EF_chrono"] = np.nan

    return df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Compute stock-difference and chronosequence EF."
    )
    parser.add_argument("--input", required=True, help="Path to dataset with SEQI_star")
    parser.add_argument("--output", required=True, help="Path to save EF results")
    parser.add_argument("--cref_global", type=float, default=13.0,
                        help="Global fallback baseline C_ref (t C ha^-1)")

    args = parser.parse_args()

    in_path = Path(args.input)
    if in_path.suffix.lower() in [".xlsx", ".xlsm"]:
        df_in = pd.read_excel(in_path)
    else:
        df_in = pd.read_csv(in_path)

    df_out = compute_efs(df_in, cref_global=args.cref_global)

    out_path = Path(args.output)
    if out_path.suffix.lower() in [".xlsx", ".xlsm"]:
        df_out.to_excel(out_path, index=False)
    else:
        df_out.to_csv(out_path, index=False)

    print(f"Saved EF results to: {out_path}")
