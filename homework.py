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
    save_plot, SCHOOL_COL, TERRITORY_COL, GENDER_COL, HUM_SUBJECTS, TECH_SUBJECTS, add_mean_score, add_group_score, get_gender_metrics
)


def analyze_best_schools(df, subjects=None, group_name="Overall", min_students=20, top_n=10):
    print(f"\n--- Top Schools Multicriteria Ideal Point ({group_name}) ---")

    if subjects is None:
        score_cols = get_score_columns(df)
    else:
        score_cols = [c for c in subjects if c in df.columns]

    if not score_cols:
        return

    df = df.copy()

    # Aggregate by school to find average scores per dimensional subject dot
    school_means = df.groupby(SCHOOL_COL)[score_cols].mean()
    
    school_counts = df.groupby(SCHOOL_COL)[score_cols].count().sum(axis=1)
    valid_schools = school_counts[school_counts >= min_students].index

    school_means = school_means.loc[valid_schools]

    school_means = school_means.fillna(0)
    ideal_point = school_means.max()

    distances = np.sqrt(((school_means - ideal_point) ** 2).sum(axis=1))
    top_schools = distances.sort_values(ascending=True).head(top_n)

    result = pd.DataFrame({
        "Distance to Ideal": top_schools,
        "Total Exams": school_counts.loc[top_schools.index]
    })
    
    print(f"Absolute winner is {result}")


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


def plot_gender_subject_patterns(df, label="overall"):
    ensure_dir("plots/homework/gender")

    result = get_gender_metrics(df).sort_values("male_%", ascending=False)
    if result.empty: return

    x = np.arange(len(result))

    plt.figure(figsize=(12, 6))

    plt.bar(x - 0.2, result["male_%"], width=0.4, label="Male")
    plt.bar(x + 0.2, result["female_%"], width=0.4, label="Female")

    plt.xticks(x, result["subject"], rotation=45, ha='right')
    plt.legend()

    save_plot(
        f"plots/homework/gender/gender_subject_distribution_{label.lower()}.png",
        f"Gender Participation by Subject ({label})",
        "Subject",
        "Participation %",
    )


def analyze_subject_difficulty(df):
    print("\n--- Subject Difficulty ---")

    score_cols = get_score_columns(df)
    difficulty = df[score_cols].mean().sort_values(ascending=False)

    print(difficulty)


def plot_urban_vs_rural(df):
    ensure_dir("plots/homework/progression")

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

    if "місто" in grouped.columns:
        plt.plot(grouped.index, grouped["місто"], marker='o', label="City")
    if "селище, село" in grouped.columns:
        plt.plot(grouped.index, grouped["селище, село"], marker='o', label="Village")

    plt.title("City vs Village Performance Over Time")
    plt.xlabel("Year")
    plt.ylabel("Mean Score")
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("plots/homework/progression/urban_vs_rural.png")
    plt.close()

    if "місто" in grouped.columns and "селище, село" in grouped.columns:
        gap = grouped["місто"] - grouped["селище, село"]

        plt.figure(figsize=(10, 6))
        plt.plot(gap.index, gap.values, marker='o')

        plt.title("Urban - Rural Performance Gap Over Time")
        plt.xlabel("Year")
        plt.ylabel("Score Difference")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig("plots/homework/progression/urban_rural_gap.png")
        plt.close()


def plot_gender_bias(df, label="overall"):
    ensure_dir("plots/homework/gender")

    result = get_gender_metrics(df).sort_values("bias", ascending=False)
    if result.empty: return

    plt.figure(figsize=(10, 6))
    plt.barh(result["subject"], result["bias"])

    save_plot(
        f"plots/homework/gender/gender_bias_{label.lower()}.png",
        f"Gender Bias by Subject (>1 = male skew) ({label})",
        "Bias",
        "Subject",
    )


def plot_top_schools_trend(df, subjects=None, group_name="Overall", top_n=20, min_students=20):
    ensure_dir("plots/homework/progression")

    df = add_group_score(df, subjects)
    if df is None:
        return

    stats = (
        df.groupby(["Year", SCHOOL_COL])
        .agg(
            avg_score=("group_score", "mean"),
            students=("group_score", "count"),
        )
        .reset_index()
    )

    stats = stats[stats["students"] >= min_students]
    if stats.empty: return

    pivot = stats.pivot(index="Year", columns=SCHOOL_COL, values="avg_score")

    # drop schools with missing years (port from investigation)
    pivot = pivot.dropna(axis=1)

    top_schools = (
        pivot.mean()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )

    pivot = pivot[top_schools]

    plt.figure(figsize=(18, 10))

    pivot.plot(ax=plt.gca(), marker='o', colormap='tab20')

    plt.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, -0.2),
        ncol=2,
        fontsize=8
    )

    save_plot(
        f"plots/homework/progression/top_schools_trend_{group_name.lower()}.png",
        f"Top Schools Performance Over Time ({group_name})",
        "Year",
        "Score",
        xticks=pivot.index
    )


if __name__ == "__main__":
    frames = []

    for path in AGGREGATION:
        year = extract_year(path)
        print(f"Loading {path} ({year})...")

        df = clean_and_rename(read_prepared(path))
        df["Year"] = year
        frames.append(df)

    full_df = pd.concat(frames, ignore_index=True)

    analyze_best_schools(full_df, subjects=None, group_name="All Subjects")
    analyze_best_schools(full_df, subjects=HUM_SUBJECTS, group_name="Humanities")
    analyze_best_schools(full_df, subjects=TECH_SUBJECTS, group_name="Tech")
    analyze_urban_vs_rural(full_df)
    analyze_subject_difficulty(full_df)

    print("\nGenerating plots.")
    plot_top_schools_trend(full_df, subjects=HUM_SUBJECTS, group_name="Humanities")
    plot_top_schools_trend(full_df, subjects=TECH_SUBJECTS, group_name="Tech")
    plot_urban_vs_rural(full_df)

    plot_gender_subject_patterns(full_df, label="Overall")
    plot_gender_bias(full_df, label="Overall")

    for year, group in full_df.groupby("Year"):
        plot_gender_subject_patterns(group, label=str(year))
        plot_gender_bias(group, label=str(year))

    print("Done.")
