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
    save_plot,
)


# --- helpers -----------------------------------------------------------------

def run_yearly_analysis(df, func, title):
    print(f"\n===== {title} (Yearly) =====")
    for year, group in sorted(df.groupby("Year")):
        print(f"\n--- {year} ---")
        func(group)


# --- analysis ---------------------------------------------------------------

def analyze_best_schools(df):
    print("\n--- Top Schools ---")

    school_col = 'Заклад освіти учасника'
    score_cols = get_score_columns(df)

    df = df.copy()
    df['student_mean'] = df[score_cols].mean(axis=1)

    stats = (
        df.groupby(school_col)
        .agg(avg_score=('student_mean', 'mean'),
             students=('student_mean', 'size'))
    )

    top = (
        stats[stats['students'] >= 20]
        .sort_values('avg_score', ascending=False)
        .head(10)
    )

    print(top)


def analyze_urban_vs_rural(df):
    print("\n--- Urban vs Rural ---")

    territory_col = 'Тип території'
    score_cols = get_score_columns(df)

    df = df.copy()
    df['overall_score'] = df[score_cols].mean(axis=1)

    comparison = df.groupby(territory_col)['overall_score'].mean().sort_index()
    print(comparison)

    city = comparison.get('місто')
    village = comparison.get('селище, село')

    if city is not None and village is not None:
        print(f"Gap: {city - village:.2f}")


def analyze_gender_subject_patterns(df):
    print("\n--- Gender & Subject Preferences ---")

    gender_col = 'Стать'
    score_cols = get_score_columns(df)

    gender_totals = df[gender_col].value_counts()
    rows = []

    for subject in score_cols:
        participants = df[df[subject].notna()]
        counts = participants[gender_col].value_counts()

        male_ratio = counts.get('чоловіча', 0) / gender_totals.get('чоловіча', 1)
        female_ratio = counts.get('жіноча', 0) / gender_totals.get('жіноча', 1)

        rows.append({
            'subject': subject,
            'male_%': round(male_ratio * 100, 1),
            'female_%': round(female_ratio * 100, 1),
            'male_bias': round(male_ratio / female_ratio, 2) if female_ratio else np.inf,
        })

    result = pd.DataFrame(rows).sort_values('male_bias', ascending=False)
    print(result)


def analyze_subject_difficulty(df):
    print("\n--- Subject Difficulty ---")

    score_cols = get_score_columns(df)
    difficulty = df[score_cols].mean().sort_values(ascending=False)

    print(difficulty)


# --- visualizations ---------------------------------------------------------

def plot_overall_trend(df):
    ensure_dir("plots/progression/analysis")

    score_cols = get_score_columns(df)

    yearly = (
        df.assign(mean_score=df[score_cols].mean(axis=1))
          .groupby("Year")["mean_score"]
          .mean()
    )

    plt.figure()
    plt.plot(yearly.index, yearly.values, marker='o')

    save_plot(
        "plots/progression/overall_trend.png",
        "Average Score Over Time",
        "Year",
        "Score",
        xticks=yearly.index
    )


def plot_subject_trends(df):
    ensure_dir("plots/progression")

    score_cols = get_score_columns(df)
    yearly = df.groupby("Year")[score_cols].mean()

    for subject in score_cols:
        plt.figure()
        plt.plot(yearly.index, yearly[subject], marker='o')

        save_plot(
            f"plots/progression/{subject}.png",
            f"{subject} Trend",
            "Year",
            "Score",
            xticks=yearly.index
        )


def plot_urban_rural_trend(df):
    ensure_dir("plots/progression")

    score_cols = get_score_columns(df)

    df = df.copy()
    df["mean_score"] = df[score_cols].mean(axis=1)

    grouped = df.groupby(["Year", "Тип території"])["mean_score"].mean().unstack()

    plt.figure()

    if "місто" in grouped:
        plt.plot(grouped.index, grouped["місто"], marker='o', label="City")

    if "селище, село" in grouped:
        plt.plot(grouped.index, grouped["селище, село"], marker='o', label="Village")

    plt.legend()

    save_plot(
        "plots/progression/urban_vs_rural.png",
        "Urban vs Rural Scores Over Time",
        "Year",
        "Score",
        xticks=grouped.index
    )

    if "місто" in grouped and "селище, село" in grouped:
        gap = grouped["місто"] - grouped["селище, село"]

        plt.figure()
        plt.plot(gap.index, gap.values, marker='o')

        save_plot(
            "plots/progression/urban_rural_gap.png",
            "Urban - Rural Gap",
            "Year",
            "Score Difference",
            xticks=gap.index
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
        "plots/top_schools.png",
        "Top Schools",
        "Score",
        "School"
    )


def plot_gender_participation(df):
    ensure_dir("plots/gender")

    gender_col = "Стать"
    score_cols = get_score_columns(df)

    rows = []

    for subject in score_cols:
        participants = df[df[subject].notna()]
        counts = participants[gender_col].value_counts()

        rows.append({
            "subject": subject,
            "male": counts.get("чоловіча", 0),
            "female": counts.get("жіноча", 0),
        })

    data = pd.DataFrame(rows).set_index("subject")

    plt.figure()
    data.plot(kind="bar")

    save_plot(
        "plots/gender/participation.png",
        "Gender Participation by Subject",
        "Subject",
        "Students"
    )

def plot_top_schools_trend(df, top_n=10, min_students=20):
    ensure_dir("plots/progression")

    school_col = 'Заклад освіти учасника'
    score_cols = get_score_columns(df)

    df = df.copy()
    df["mean_score"] = df[score_cols].mean(axis=1)

    # --- yearly stats per school
    stats = (
        df.groupby(["Year", school_col])
        .agg(
            avg_score=("mean_score", "mean"),
            students=("mean_score", "size")
        )
        .reset_index()
    )

    # --- filter by minimum students per year
    stats = stats[stats["students"] >= min_students]

    # --- pivot for time series
    pivot = stats.pivot(index="Year", columns=school_col, values="avg_score")

    # --- drop schools with missing years (your requirement)
    pivot = pivot.dropna(axis=1)

    if pivot.empty:
        print("No schools with consistent yearly data.")
        return

    # --- select top schools by overall mean
    top_schools = pivot.mean().sort_values(ascending=False).head(top_n).index
    pivot = pivot[top_schools]

    # --- plot
    plt.figure()

    for school in pivot.columns:
        plt.plot(pivot.index, pivot[school], marker='o', label=school)

    plt.legend(fontsize=6)

    save_plot(
        "plots/progression/top_schools_trend.png",
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

    analyze_best_schools(full_df)
    analyze_urban_vs_rural(full_df)
    analyze_gender_subject_patterns(full_df)
    analyze_subject_difficulty(full_df)

    # --- yearly breakdown ----------------------------------------------------

    run_yearly_analysis(full_df, analyze_best_schools, "Top Schools")
    run_yearly_analysis(full_df, analyze_urban_vs_rural, "Urban vs Rural")
    run_yearly_analysis(full_df, analyze_gender_subject_patterns, "Gender Patterns")
    run_yearly_analysis(full_df, analyze_subject_difficulty, "Subject Difficulty")

    # --- visualizations ------------------------------------------------------

    print("\nGenerating plots...")

    plot_overall_trend(full_df)
    plot_subject_trends(full_df)
    plot_urban_rural_trend(full_df)
    plot_top_schools_trend(full_df)
    plot_gender_participation(full_df)

    print("Plots saved to /plots")