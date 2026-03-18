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

SCHOOL_COL = 'Заклад освіти учасника'
GENDER_COL = 'Стать'
TERRITORY_COL = 'Тип території'


def add_mean_score(df):
    df = df.copy()
    score_cols = get_score_columns(df)
    df["mean_score"] = df[score_cols].mean(axis=1)
    return df


def run_yearly_analysis(df, func, title):
    print(f"\n===== {title} (Yearly) =====")
    for year, group in sorted(df.groupby("Year")):
        print(f"\n--- {year} ---")
        func(group)


# --- analysis ---------------------------------------------------------------

def analyze_best_schools(df, min_students=20, top_n=10):
    print("\n--- Top Schools ---")

    df = add_mean_score(df)

    stats = (
        df.groupby(SCHOOL_COL)
        .agg(
            avg_score=("mean_score", "mean"),
            students=("mean_score", "size"),
        )
    )

    top = (
        stats[stats["students"] >= min_students]
        .sort_values("avg_score", ascending=False)
        .head(top_n)
    )

    print(top)


def analyze_urban_vs_rural(df):
    print("\n--- Urban vs Rural ---")

    df = add_mean_score(df)

    comparison = (
        df.groupby(TERRITORY_COL)["mean_score"]
        .mean()
        .sort_index()
    )

    print(comparison)

    city = comparison.get('місто')
    village = comparison.get('селище, село')

    if city is not None and village is not None:
        print(f"Gap: {city - village:.2f}")


def plot_gender_subject_patterns(df):
    ensure_dir("plots/homework/gender")

    score_cols = get_score_columns(df)
    gender_totals = df[GENDER_COL].value_counts()

    rows = []

    for subject in score_cols:
        participants = df[df[subject].notna()]
        counts = participants[GENDER_COL].value_counts()

        male_ratio = counts.get('чоловіча', 0) / gender_totals.get('чоловіча', 1)
        female_ratio = counts.get('жіноча', 0) / gender_totals.get('жіноча', 1)

        rows.append({
            "subject": subject,
            "male_%": male_ratio * 100,
            "female_%": female_ratio * 100,
        })

    result = pd.DataFrame(rows).sort_values("male_%", ascending=False)

    x = np.arange(len(result))

    plt.figure(figsize=(12, 6))

    plt.bar(x - 0.2, result["male_%"], width=0.4, label="Male")
    plt.bar(x + 0.2, result["female_%"], width=0.4, label="Female")

    plt.xticks(x, result["subject"], rotation=45, ha='right')
    plt.legend()

    save_plot(
        "plots/gender/gender_subject_distribution.png",
        "Gender Participation by Subject",
        "Subject",
        "Participation %",
    )


def analyze_subject_difficulty(df):
    print("\n--- Subject Difficulty ---")

    score_cols = get_score_columns(df)
    difficulty = df[score_cols].mean().sort_values(ascending=False)

    print(difficulty)


def plot_urban_vs_rural(df):
    ensure_dir("plots/progression")

    df = add_mean_score(df)

    grouped = (
        df.groupby(["Year", TERRITORY_COL])["mean_score"]
        .mean()
        .unstack()
    )

    if grouped.empty:
        print("No data for urban/rural plot.")
        return

    plt.figure(figsize=(10, 6))

    for col in grouped.columns:
        plt.plot(grouped.index, grouped[col], marker='o', label=col)

    plt.legend()

    save_plot(
        "plots/progression/urban_vs_rural.png",
        "Urban vs Rural Performance Over Time",
        "Year",
        "Score",
        xticks=grouped.index
    )


def plot_gender_bias(df):
    ensure_dir("plots/gender")

    score_cols = get_score_columns(df)
    gender_totals = df[GENDER_COL].value_counts()

    rows = []

    for subject in score_cols:
        participants = df[df[subject].notna()]
        counts = participants[GENDER_COL].value_counts()

        male_ratio = counts.get('чоловіча', 0) / gender_totals.get('чоловіча', 1)
        female_ratio = counts.get('жіноча', 0) / gender_totals.get('жіноча', 1)

        bias = male_ratio / female_ratio if female_ratio else np.nan

        rows.append({
            "subject": subject,
            "bias": bias
        })

    result = pd.DataFrame(rows).sort_values("bias", ascending=False)

    plt.figure(figsize=(10, 6))
    plt.barh(result["subject"], result["bias"])

    save_plot(
        "plots/gender/gender_bias.png",
        "Gender Bias by Subject (>1 = male skew)",
        "Bias",
        "Subject",
    )


def plot_top_schools_trend(df, top_n=10, min_students=20):
    ensure_dir("plots/progression")

    df = add_mean_score(df)

    stats = (
        df.groupby(["Year", SCHOOL_COL])
        .agg(
            avg_score=("mean_score", "mean"),
            students=("mean_score", "size"),
        )
        .reset_index()
    )

    stats = stats[stats["students"] >= min_students]

    pivot = stats.pivot(index="Year", columns=SCHOOL_COL, values="avg_score")

    # don't drop schools that don't have full timeline
    pivot = pivot.mean(skipna=True)

    top_schools = (
        pivot.mean()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )

    pivot = pivot[top_schools]

    plt.figure(figsize=(14, 8))

    for school in pivot.columns:
        plt.plot(pivot.index, pivot[school], marker='o', label=school)

    plt.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, -0.2),
        ncol=2,
        fontsize=8
    )

    save_plot(
        "plots/progression/top_schools_trend.png",
        "Top Schools Performance Over Time",
        "Year",
        "Score",
        xticks=pivot.index
    )


# --- main --------------------------------------------------------------------

if __name__ == "__main__":
    frames = []

    for path in AGGREGATION:
        year = extract_year(path)
        print(f"Loading {path} ({year})...")

        df = clean_and_rename(read_prepared(path))
        df["Year"] = year
        frames.append(df)

    full_df = pd.concat(frames, ignore_index=True)

    analyze_best_schools(full_df)
    analyze_urban_vs_rural(full_df)
    plot_gender_subject_patterns(full_df)
    analyze_subject_difficulty(full_df)
    plot_gender_bias(full_df)

    run_yearly_analysis(full_df, analyze_best_schools, "Top Schools")
    run_yearly_analysis(full_df, analyze_urban_vs_rural, "Urban vs Rural")
    run_yearly_analysis(full_df, plot_gender_subject_patterns, "Gender Patterns")
    run_yearly_analysis(full_df, analyze_subject_difficulty, "Subject Difficulty")

    print("\nGenerating plots...")
    plot_top_schools_trend(full_df)
    plot_urban_vs_rural(full_df)
    print("Done.")
