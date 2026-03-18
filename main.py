import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from utils import get_score_columns, ensure_dir, save_plot, sanitize_filename, prepare_years, fit_and_predict, \
    setup_dirs, AGGREGATION, clean_and_rename, read_prepared


def generate_all_plots(df: pd.DataFrame, label: str):
    print(f"\n--- {label}: generating plots ---")

    score_cols = get_score_columns(df)
    if not score_cols:
        print("No score columns found.")
        return

    plot_distributions(df, score_cols, label)
    plot_gender_boxplots(df, score_cols, label)
    plot_correlation(df, score_cols, label)


def plot_distributions(df, score_cols, label):
    ensure_dir("plots/distributions")
    plt.figure(figsize=(15, 8))

    for col in score_cols:
        data = df[col].dropna()
        data = data[(100 <= data) & (data <= 200)]
        if not data.empty:
            plt.hist(data, bins=50, range=(100, 200), alpha=0.4, label=col)

    plt.legend(bbox_to_anchor=(1.05, 1))

    save_plot(
        f"plots/distributions/dist_{label}.png",
        f"Score distributions — {label}",
        "Score",
        "Frequency",
        grid_alpha=0.2
    )


def plot_gender_boxplots(df, score_cols, label):
    sex_col = "Стать"
    if sex_col not in df.columns:
        return

    base_path = f"plots/gender/{label}"
    ensure_dir(base_path)

    for subject in score_cols:
        subset = df[[sex_col, subject]].dropna()
        if subset.empty:
            continue

        plt.figure(figsize=(10, 6))
        subset.boxplot(column=subject, by=sex_col)

        plt.suptitle("")
        plt.ylim(100, 210)

        save_plot(
            f"{base_path}/box_{sanitize_filename(subject)}.png",
            f"{subject} by gender — {label}",
            "",
            "Score"
        )


def plot_correlation(df, score_cols, label):
    if len(score_cols) < 2:
        return

    ensure_dir("plots/correlations")

    corr = df[score_cols].corr()

    plt.figure(figsize=(12, 10))
    plt.imshow(corr, cmap="RdYlGn", vmin=-1, vmax=1)
    plt.colorbar(label="Correlation")

    plt.xticks(range(len(score_cols)), score_cols, rotation=90)
    plt.yticks(range(len(score_cols)), score_cols)

    for i in range(len(score_cols)):
        for j in range(len(score_cols)):
            val = corr.iloc[i, j]
            text = "N/A" if np.isnan(val) else f"{val:.2f}"
            color = "gray" if np.isnan(val) else ("white" if abs(val) > 0.7 else "black")

            plt.text(j, i, text, ha="center", va="center", fontsize=8, color=color)

    save_plot(
        f"plots/correlations/corr_{label}.png",
        f"Correlation matrix — {label}",
        "",
        ""
    )


# --- progression -------------------------------------------------------------

def plot_subject_progression(summary, forecast_years=2):
    ensure_dir("plots/progression/subjects")

    df = pd.DataFrame(summary).sort_values("Year")
    subjects = [c for c in df.columns if c not in ("Year", "Region")]

    years, future, all_years = prepare_years(df, forecast_years)

    plt.figure(figsize=(15, 10))

    for subject in subjects:
        series = df.groupby("Year")[subject].mean().dropna()
        if len(series) < 2:
            continue

        x = series.index.to_numpy().reshape(-1, 1)
        y = series.values

        model, y_all = fit_and_predict(x, y, all_years)

        line, = plt.plot(series.index, y, marker="o", label=subject)

        forecast_x = future.reshape(-1, 1)
        forecast_y = model.predict(forecast_x)

        plt.plot(
            future,
            forecast_y,
            linestyle=":",
            alpha=0.6,
            color=line.get_color()
        )

    plt.legend(bbox_to_anchor=(1.05, 1))

    save_plot(
        "plots/progression/subjects_combined_forecast.png",
        f"Subject progression (+{forecast_years}y forecast)",
        "Year",
        "Mean score",
        xticks=all_years.flatten()
    )


def plot_all_regions_progression(data, forecast_years=2):
    ensure_dir("plots/progression")

    df = pd.DataFrame(data)
    years, future, all_years = prepare_years(df, forecast_years)

    plt.figure(figsize=(15, 10))

    # regional lines
    for _, group in df.groupby("Region"):
        group = group.sort_values("Year")
        if len(group) < 2:
            continue

        plt.plot(group["Year"], group["Avg_Score"], marker="o", alpha=0.25)

    # global trend
    yearly_avg = df.groupby("Year")["Avg_Score"].mean()

    if len(yearly_avg) >= 2:
        x = yearly_avg.index.to_numpy().reshape(-1, 1)
        y = yearly_avg.values

        model, y_all = fit_and_predict(x, y, all_years)

        plt.plot(
            years,
            y_all[:len(years)],
            linewidth=3,
            label=f"Global trend (slope={model.coef_[0]:.2f})"
        )

        plt.plot(
            future,
            y_all[-len(future):],
            linestyle="--",
            linewidth=3,
            label=f"{forecast_years}-year forecast"
        )

    plt.legend(bbox_to_anchor=(1.05, 1))

    save_plot(
        "plots/progression/all_regions_forecast.png",
        f"Regional progression (+{forecast_years}y forecast)",
        "Year",
        "Mean score",
        xticks=all_years.flatten(),
        grid_alpha=0.4
    )


# --- main --------------------------------------------------------------------

if __name__ == "__main__":
    setup_dirs()

    national = []
    regional = []
    all_data = []

    for path in AGGREGATION:
        if not os.path.exists(path):
            print(f"Skipping missing file: {path}")
            continue

        year_str = "".join(filter(str.isdigit, os.path.basename(path)))
        year = int(year_str) if year_str else 0

        print(f"\nProcessing {year}...")

        try:
            df = clean_and_rename(read_prepared(path))
            score_cols = get_score_columns(df)

            if not score_cols:
                continue

            df["Рік_Датасету"] = year
            all_data.append(df)

            generate_all_plots(df, str(year))

            # national stats
            stats = df[score_cols].mean().to_dict()
            stats["Year"] = year
            national.append(stats)

            # regional stats
            region_col = "Регіон реєстрації/проживання учасника"
            if region_col in df.columns:
                df["Temp_Avg"] = df[score_cols].mean(axis=1)
                grouped = df.groupby(region_col)["Temp_Avg"].mean()

                for region_name, value in grouped.items():
                    regional.append({
                        "Region": region_name,
                        "Avg_Score": value,
                        "Year": year,
                    })

            print(f"Done {year} ({len(df)} rows)")

        except Exception as e:
            print(f"Error in {year}: {e}")

    # agg data
    if all_data:
        print("\nRunning aggregate analysis...")
        combined = pd.concat(all_data, ignore_index=True)
        generate_all_plots(combined, "aggregate")

    if national:
        plot_subject_progression(national)

    if regional:
        plot_all_regions_progression(regional)

    print("\nAll plots generated → see 'plots/'")
