"""
04_mapping.py

Create a quick map of EF_chrono using latitude/longitude.
"""

import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path

from 01_load_clean import COL_LAT, COL_LON


def plot_ef_map(df: pd.DataFrame, out_path: str):
    proj = ccrs.PlateCarree()
    fig = plt.figure(figsize=(10, 6))
    ax = plt.axes(projection=proj)

    # Basemap
    ax.add_feature(cfeature.LAND, facecolor="lightgrey")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3)
    ax.add_feature(cfeature.OCEAN, facecolor="azure")

    # Indonesia-ish extent (adjust if needed)
    ax.set_extent([94, 142, -12, 8], crs=proj)

    # Plot EF_chrono
    m = ax.scatter(
        df[COL_LON],
        df[COL_LAT],
        c=df["EF_chrono"],
        cmap="viridis",
        s=60,
        edgecolors="black",
        transform=proj,
    )

    cbar = plt.colorbar(m, ax=ax, orientation="horizontal", pad=0.08, shrink=0.7)
    cbar.set_label("EF_chrono (t C ha$^{-1}$ yr$^{-1}$)")

    plt.title("Seagrass Carbon Emission Factors (Chronosequence-based)")

    out_path = Path(out_path)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved map to: {out_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Plot EF_chrono map from EF results file."
    )
    parser.add_argument("--input", required=True, help="Path to EF results Excel/CSV")
    parser.add_argument("--output", required=True, help="Output image (e.g., .png, .pdf)")

    args = parser.parse_args()

    in_path = Path(args.input)
    if in_path.suffix.lower() in [".xlsx", ".xlsm"]:
        df_in = pd.read_excel(in_path)
    else:
        df_in = pd.read_csv(in_path)

    plot_ef_map(df_in, args.output)
