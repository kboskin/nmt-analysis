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
    save_plot, run_yearly_analysis, get_gender_metrics
)
import matplotlib.patches as mpatches


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


def plot_gender_candle_chart(df, label="overall"):
    ensure_dir("plots/investigation/gender")
    
    score_cols = get_score_columns(df)
    gender_col = 'Стать'
    
    plt.figure(figsize=(18, 8))
    
    positions = []
    labels = []
    data = []
    
    for i, subject in enumerate(score_cols):
        subject_data = df.dropna(subset=[subject, gender_col])

        # filter >100, to avoid dropouts
        subject_data = subject_data[subject_data[subject] >= 100]
        
        male_scores = subject_data[subject_data[gender_col] == 'чоловіча'][subject].values
        female_scores = subject_data[subject_data[gender_col] == 'жіноча'][subject].values
        
        if len(male_scores) > 10 and len(female_scores) > 10:
            data.extend([male_scores, female_scores])
            # add some margins here and there
            positions.extend([i*3 - 0.5, i*3 + 0.5])
            labels.append(subject)

    bplot = plt.boxplot(data, positions=positions, patch_artist=True, widths=0.8)
    
    colors = ['lightblue', 'lightpink'] * (len(data) // 2)
    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)

    # add some margins here and there for ticks
    plt.xticks([i*3 for i in range(len(labels))], labels, rotation=45, ha='right')
    plt.title(f"Score Distribution by Gender (Candle/Boxplot) ({label})")
    plt.ylabel("Score")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    male_patch = mpatches.Patch(color='lightblue', label='Male')
    female_patch = mpatches.Patch(color='lightpink', label='Female')
    plt.legend(handles=[male_patch, female_patch])
    
    plt.savefig(f"plots/investigation/gender/gender_candle_{label.lower()}.png")
    plt.close()


def plot_top_schools_trend(df, top_n=10, min_students=10):
    ensure_dir("plots/investigation/progression")

    school_col = 'Заклад освіти учасника'
    score_cols = get_score_columns(df)

    df = df.copy()
    df["mean_score"] = df[score_cols].mean(axis=1)

    # Calculate per-year students
    yearly_stats = df.groupby(["Year", school_col]).agg(
        students=("mean_score", "count")
    ).reset_index()

    students_pivot = yearly_stats.pivot(index="Year", columns=school_col, values="students")
    
    # Valid schools must have >= min_students FOR ALL THE YEARS
    total_years = df["Year"].nunique()
    valid_mask = (students_pivot >= min_students).sum() == total_years
    valid_school_names = valid_mask[valid_mask].index

    overall_stats = (
        df[df[school_col].isin(valid_school_names)]
        .groupby(school_col)
        .agg(
            avg_score=("mean_score", "mean"),
        )
    )

    top_school_names = overall_stats.sort_values("avg_score", ascending=False).head(top_n).index

    df_top = df[df[school_col].isin(top_school_names)]
    stats = (
        df_top.groupby(["Year", school_col])
        .agg(avg_score=("mean_score", "mean"))
        .reset_index()
    )

    pivot = stats.pivot(index="Year", columns=school_col, values="avg_score")
    pivot = pivot[top_school_names]

    plt.figure(figsize=(20, 10))

    for school in pivot.columns:
        plt.plot(pivot.index, pivot[school], marker='o', label=school)

    plt.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, -0.2),
        ncol=2,
        fontsize=8
    )

    save_plot(
        f"plots/investigation/progression/top_schools_trend.png",
        "Top Schools Performance Over Time",
        "Year",
        "Score",
        xticks=pivot.index
    )


if __name__ == "__main__":
    data = []

    for path in AGGREGATION:

        year = extract_year(path)
        print(f"Loading {path} ({year})...")

        df = clean_and_rename(read_prepared(path))
        df["Year"] = year
        data.append(df)

    full_df = pd.concat(data, ignore_index=True)

    print("\nGenerating plots...")

    plot_subject_distributions(full_df, label="overall")
    for year, group in full_df.groupby("Year"):
        plot_subject_distributions(group, label=str(year))

    plot_gender_candle_chart(full_df, label="overall")
    for year, group in full_df.groupby("Year"):
        plot_gender_candle_chart(group, label=str(year))

    plot_overall_trend(full_df)
    plot_subject_trends(full_df)

    print("Plots saved to /plots")
