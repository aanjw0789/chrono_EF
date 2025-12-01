"""
02_seqi_model.py

SEQI handling and (optional) modelling. For now, SEQI is passed
through as observed; missing values are left as NaN or can be
filled with simple rules.
"""

import pandas as pd
from pathlib import Path

from 01_load_clean import COL_SEQI  # reuse constant


def add_effective_seqi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Define SEQI_i* (effective SEQI):

    For now:
        SEQI_i* = SEQI_i  (if observed)
        remains NaN if missing.

    Later, RF/regression imputation can be added here.

    Returns the DataFrame with a new column 'SEQI_star'.
    """
    df = df.copy()
    df["SEQI_star"] = df[COL_SEQI]

    # Example of very simple fill (optional):
    # df["SEQI_star"] = df["SEQI_star"].fillna(df["SEQI_star"].median())

    return df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Add effective SEQI (SEQI_star) to cleaned dataset."
    )
    parser.add_argument("--input", required=True, help="Path to cleaned CSV/Excel")
    parser.add_argument("--output", required=True, help="Path to save updated file")

    args = parser.parse_args()

    in_path = Path(args.input)
    if in_path.suffix.lower() in [".xlsx", ".xlsm"]:
        df_in = pd.read_excel(in_path)
    else:
        df_in = pd.read_csv(in_path)

    df_out = add_effective_seqi(df_in)

    out_path = Path(args.output)
    if out_path.suffix.lower() in [".xlsx", ".xlsm"]:
        df_out.to_excel(out_path, index=False)
    else:
        df_out.to_csv(out_path, index=False)

    print(f"Saved dataset with SEQI_star to: {out_path}")
