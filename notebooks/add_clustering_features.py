"""
Add extra engagement features for clustering analysis.

Features added (not already in ews_feature_store.csv):
- clicks_vs_cohort: Relative engagement vs cohort average
- clicks_velocity: Week-over-week change in weekly clicks (acceleration)
- last_active_day: Most recent activity day (cumulative max)
- days_since_last_activity: Days since last activity relative to week end
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
PROC_DIR = Path("..") / "data" / "processed"
RAW_DIR = Path("..") / "data" / "raw"

KEY_COLS = ["student_id", "code_module", "code_presentation"]

def main():
    # Load feature store
    print("Loading ews_feature_store.csv...")
    df = pd.read_csv(PROC_DIR / "ews_feature_store.csv")
    print(f"Shape: {df.shape}")

    # Load raw student_vle for activity dates
    print("Loading student_vle.csv for activity dates...")
    student_vle = pd.read_csv(RAW_DIR / "studentVle.csv")

    # -------------------------------------------------------------------------
    # 1. Clicks vs cohort (relative engagement)
    # -------------------------------------------------------------------------
    if "clicks_vs_cohort" not in df.columns:
        cohort_avg = df.groupby(["code_module", "code_presentation", "week"], as_index=False)["cum_clicks_total"].mean()
        cohort_avg = cohort_avg.rename(columns={"cum_clicks_total": "cohort_avg"})
        df = df.merge(cohort_avg, on=["code_module", "code_presentation", "week"], how="left")
        df["clicks_vs_cohort"] = np.where(df["cohort_avg"] > 0, df["cum_clicks_total"] / df["cohort_avg"], 0)
        df = df.drop(columns=["cohort_avg"])
        print("Added: clicks_vs_cohort")

    # -------------------------------------------------------------------------
    # 2. Clicks velocity (week-over-week change in weekly clicks)
    # -------------------------------------------------------------------------
    if "clicks_velocity" not in df.columns:
        df = df.sort_values(KEY_COLS + ["week"])
        df["clicks_velocity"] = df.groupby(KEY_COLS)["delta_clicks_total"].diff().fillna(0)
        print("Added: clicks_velocity")

    # -------------------------------------------------------------------------
    # 3. Last active day & days since last activity
    # -------------------------------------------------------------------------
    if "last_active_day" not in df.columns:
        # Process activity dates from raw data
        activity_dates = student_vle[["id_student", "code_module", "code_presentation", "date"]].copy()
        activity_dates = activity_dates.rename(columns={"id_student": "student_id"})
        activity_dates["date"] = pd.to_numeric(activity_dates["date"], errors="coerce")
        activity_dates = activity_dates.dropna(subset=["date"])
        activity_dates["week"] = (activity_dates["date"] // 7).astype(int)

        # Most recent activity day up to each week
        weekly_last_day = (
            activity_dates
            .groupby(KEY_COLS + ["week"], as_index=False)["date"]
            .max()
            .rename(columns={"date": "last_active_day"})
            .sort_values(KEY_COLS + ["week"])
        )
        weekly_last_day["last_active_day"] = weekly_last_day.groupby(KEY_COLS)["last_active_day"].cummax()

        df = df.merge(
            weekly_last_day[KEY_COLS + ["week", "last_active_day"]],
            on=KEY_COLS + ["week"],
            how="left",
        )
        df["last_active_day"] = df.groupby(KEY_COLS)["last_active_day"].ffill()
        print("Added: last_active_day")

    # -------------------------------------------------------------------------
    # 4. Days since last activity
    # -------------------------------------------------------------------------
    if "days_since_last_activity" not in df.columns:
        # Week end day = week * 7 + 6
        df["week_end_day"] = df["week"] * 7 + 6
        df["days_since_last_activity"] = df["week_end_day"] - df["last_active_day"]
        df["days_since_last_activity"] = df["days_since_last_activity"].clip(lower=0)
        df = df.drop(columns=["week_end_day"])
        print("Added: days_since_last_activity")

    # -------------------------------------------------------------------------
    # Save
    # -------------------------------------------------------------------------
    output_path = PROC_DIR / "ews_feature_store_extra.csv"
    df.to_csv(output_path, index=False)
    print(f"\nSaved: {output_path}")
    print(f"Final shape: {df.shape}")

    # Show new columns
    new_cols = ["clicks_vs_cohort", "clicks_velocity", "last_active_day", "days_since_last_activity"]
    print(f"\nNew feature summary:")
    print(df[new_cols].describe().round(2))

if __name__ == "__main__":
    main()
