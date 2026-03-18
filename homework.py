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

HUM_SUBJECTS = ['Українська мова', 'Українська література', 'Історія України', 'Англійська мова', 'Французька мова', 'Німецька мова', 'Іспанська мова']
TECH_SUBJECTS = ['Математика', 'Фізика', 'Хімія', 'Біологія', 'Географія']

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

def analyze_best_schools(df, subjects=None, group_name="Overall", min_students=20, top_n=10):
    print(f"\n--- Top Schools ({group_name}) ---")

    if subjects is None:
        score_cols = get_score_columns(df)
    else:
        score_cols = [c for c in subjects if c in df.columns]

    if not score_cols:
        return

    df = df.copy()
    has_score = df[score_cols].notna().any(axis=1)
    df = df[has_score]
    df["group_score"] = df[score_cols].mean(axis=1)

    stats = (
        df.groupby(SCHOOL_COL)
        .agg(
            avg_score=("group_score", "mean"),
            students=("group_score", "count"),
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


def plot_gender_subject_patterns(df, label="overall"):
    ensure_dir("plots/homework/gender")

    score_cols = get_score_columns(df)
    gender_totals = df[GENDER_COL].value_counts()

    # Exclude mandatory subjects that skew visualization ranges
    mandatory_subjects = ['Математика', 'Українська мова', 'Історія України']
    score_cols = [c for c in score_cols if c not in mandatory_subjects]

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


def plot_gender_bias(df, label="overall"):
    ensure_dir("plots/homework/gender")

    score_cols = get_score_columns(df)
    gender_totals = df[GENDER_COL].value_counts()

    # Exclude mandatory subjects that skew visualization ranges
    mandatory_subjects = ['Математика', 'Українська мова', 'Історія України']
    score_cols = [c for c in score_cols if c not in mandatory_subjects]

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
        f"plots/homework/gender/gender_bias_{label.lower()}.png",
        f"Gender Bias by Subject (>1 = male skew) ({label})",
        "Bias",
        "Subject",
    )


def plot_top_schools_trend(df, subjects=None, group_name="Overall", top_n=20, min_students=20):
    ensure_dir("plots/homework/progression")

    if subjects is None:
        score_cols = get_score_columns(df)
    else:
        score_cols = [c for c in subjects if c in df.columns]

    if not score_cols:
        return

    df = df.copy()
    has_score = df[score_cols].notna().any(axis=1)
    df = df[has_score]
    df["group_score"] = df[score_cols].mean(axis=1)

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

    # --- drop schools with missing years (port from investigation)
    pivot = pivot.dropna(axis=1)

    if pivot.empty:
        print(f"No schools with consistent yearly data for {group_name}.")
        return

    # --- select top schools by overall mean
    top_schools = (
        pivot.mean()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )

    pivot = pivot[top_schools]

    plt.figure(figsize=(16, 10))

    for school in pivot.columns:
        plt.plot(pivot.index, pivot[school], marker='o', label=school)

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

    if not frames:
        print("No data found.")
        exit(1)

    full_df = pd.concat(frames, ignore_index=True)

    analyze_best_schools(full_df, subjects=HUM_SUBJECTS, group_name="Humanities")
    analyze_best_schools(full_df, subjects=TECH_SUBJECTS, group_name="Tech")
    analyze_urban_vs_rural(full_df)
    analyze_subject_difficulty(full_df)

    print("\nGenerating plots...")
    plot_top_schools_trend(full_df, subjects=HUM_SUBJECTS, group_name="Humanities")
    plot_top_schools_trend(full_df, subjects=TECH_SUBJECTS, group_name="Tech")
    plot_urban_vs_rural(full_df)

    plot_gender_subject_patterns(full_df, label="Overall")
    plot_gender_bias(full_df, label="Overall")

    for year, group in full_df.groupby("Year"):
        plot_gender_subject_patterns(group, label=str(year))
        plot_gender_bias(group, label=str(year))

    print("Done.")
