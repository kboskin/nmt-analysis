import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from utils import (
    read_prepared,
    clean_and_rename,
    AGGREGATION,
    get_score_columns,
    extract_year,
    ensure_dir,
    save_plot, run_yearly_analysis,
)


def analyze_subject_difficulty(df):
    print("\n--- Subject Difficulty ---")

    score_cols = get_score_columns(df)
    difficulty = df[score_cols].mean().sort_values(ascending=False)

    print(difficulty)


def plot_overall_trend(df):
    ensure_dir("plots/investigation/progression/analysis")

    score_cols = get_score_columns(df)

    yearly = (
        df.assign(mean_score=df[score_cols].mean(axis=1))
        .groupby("Year")["mean_score"]
        .mean()
    )

    plt.figure()
    plt.plot(yearly.index, yearly.values, marker='o')

    save_plot(
        "plots/investigation/progression/overall_trend.png",
        "Average Score Over Time",
        "Year",
        "Score",
        xticks=yearly.index
    )


def plot_subject_trends(df):
    ensure_dir("plots/investigation/progression")

    score_cols = get_score_columns(df)
    yearly = df.groupby("Year")[score_cols].mean()

    for subject in score_cols:
        plt.figure()
        plt.plot(yearly.index, yearly[subject], marker='o')

        save_plot(
            f"plots/investigation/progression/{subject}.png",
            f"{subject} Trend",
            "Year",
            "Score",
            xticks=yearly.index
        )


def plot_top_schools(df):
    ensure_dir("plots")

    school_col = 'Заклад освіти учасника'
    score_cols = get_score_columns(df)

    df = df.copy()
    df["mean_score"] = df[score_cols].mean(axis=1)

    stats = (
        df.groupby(school_col)
        .agg(avg_score=("mean_score", "mean"),
             students=("mean_score", "size"))
    )

    top = (
        stats[stats["students"] >= 20]
        .sort_values("avg_score", ascending=False)
        .head(10)
    )

    plt.figure()
    plt.barh(top.index, top["avg_score"])
    plt.gca().invert_yaxis()

    save_plot(
        "plots/investigation/top_schools.png",
        "Top Schools",
        "Score",
        "School"
    )


def plot_subject_distributions(df, label="overall"):
    ensure_dir(f"plots/investigation/distributions/{label}")

    score_cols = get_score_columns(df)

    for subject in score_cols:
        scores = df[subject].dropna()
        if len(scores) < 10:
            continue

        plt.figure(figsize=(10, 6))
        plt.hist(scores, bins=20, range=(100, 200), edgecolor='black', alpha=0.7)
        plt.xlim(100, 200)

        save_plot(
            f"plots/investigation/distributions/{label}/{subject}.png",
            f"{subject} Score Distribution ({label})",
            "Score",
            "Number of Students"
        )


def plot_top_schools_trend(df, top_n=10, min_students=20):
    ensure_dir("plots/investigation/progression")

    school_col = 'Заклад освіти учасника'
    score_cols = get_score_columns(df)

    df = df.copy()
    df["mean_score"] = df[score_cols].mean(axis=1)

    stats = (
        df.groupby(["Year", school_col])
        .agg(
            avg_score=("mean_score", "mean"),
            students=("mean_score", "size")
        )
        .reset_index()
    )

    # filter by minimum students per year
    stats = stats[stats["students"] >= min_students]
    pivot = stats.pivot(index="Year", columns=school_col, values="avg_score")

    # we are dropping schools for missing years
    pivot = pivot.dropna(axis=1)

    if pivot.empty:
        print("No schools with consistent yearly data.")
        return

    top_schools = pivot.mean().sort_values(ascending=False).head(top_n).index
    pivot = pivot[top_schools]

    plt.figure()

    for school in pivot.columns:
        plt.plot(pivot.index, pivot[school], marker='o', label=school)

    plt.legend(fontsize=6)

    save_plot(
        "plots/investigation/progression/top_schools_trend.png",
        "Top Schools Performance Over Time",
        "Year",
        "Score",
        xticks=pivot.index
    )


# --- main --------------------------------------------------------------------

if __name__ == "__main__":
    data = []

    for path in AGGREGATION:
        if not os.path.exists(path):
            continue

        year = extract_year(path)
        print(f"Loading {path} ({year})...")

        df = clean_and_rename(read_prepared(path))
        df["Year"] = year
        data.append(df)

    if not data:
        print("No data found for analysis.")
        exit()

    full_df = pd.concat(data, ignore_index=True)

    print(f"\n===== OVERALL ANALYSIS ({len(full_df)} records) =====")

    analyze_subject_difficulty(full_df)

    run_yearly_analysis(full_df, analyze_subject_difficulty, "Subject Difficulty")

    print("\nGenerating plots...")

    plot_subject_distributions(full_df, label="overall")
    for year, group in full_df.groupby("Year"):
        plot_subject_distributions(group, label=str(year))

    plot_overall_trend(full_df)
    plot_subject_trends(full_df)
    plot_top_schools_trend(full_df)

    print("Plots saved to /plots")
