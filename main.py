import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from sklearn.linear_model import LinearRegression
from utils import read_prepared, clean_and_rename


def plot_progression(summary_df):
    """Creates progression plots with linear regression for common subjects."""
    os.makedirs('plots/progression', exist_ok=True)

    summary_df = summary_df.sort_values('Рік').dropna(subset=['Рік'])
    years = summary_df['Рік'].values.reshape(-1, 1)

    subjects = [col for col in summary_df.columns if 'Оцінка 100-200' in col]

    plt.figure(figsize=(12, 8))

    for subject in subjects:
        data = summary_df[subject].values
        # Drop years with missing data for this subject
        valid_indices = ~np.isnan(data)
        if sum(valid_indices) < 2: continue  # Need at least 2 points for trend

        y_valid = years[valid_indices]
        d_valid = data[valid_indices]

        model = LinearRegression()
        model.fit(y_valid, d_valid)
        trend = model.predict(y_valid)

        line = plt.plot(y_valid, trend, linestyle='--', alpha=0.8,
                        label=f'{subject} Trend (Slope: {model.coef_[0]:.2f})')
        plt.scatter(y_valid, d_valid, color=line[0].get_color(), alpha=0.5)

        # Save individual plot as well
        plt.figure(figsize=(8, 5))
        plt.scatter(y_valid, d_valid, color='blue')
        plt.plot(y_valid, trend, color='red', label=f'Trend line ({model.coef_[0]:.2f} pts/year)')
        plt.title(f'Progression: {subject}')
        plt.xlabel('Year')
        plt.ylabel('Average Score')
        plt.xticks(y_valid.flatten().astype(int))
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.savefig(f"plots/progression/{subject.replace(' ', '_').replace('(', '').replace(')', '')}.png")
        plt.close()

    print(f"\nSaved progression plots for: {subjects}")


if __name__ == '__main__':
    data_path = 'data'
    files = [f for f in sorted(os.listdir(data_path)) if f.endswith('.csv')]

    aggregated_results = []

    for filename in files:
        print(f"Loading {filename}...")
        file_path = os.path.join(data_path, filename)

        # Extract year from filename
        year_str = ''.join(filter(str.isdigit, filename))
        year = int(year_str) if year_str else 0

        try:
            df = read_prepared(file_path)
            df = clean_and_rename(df)

            # Group by year (from filename) and calculate averages for score columns
            score_cols = [col for col in df.columns if 'Оцінка 100-200' in col]

            if score_cols:
                summary = df[score_cols].mean().to_dict()
                summary['Рік'] = year
                aggregated_results.append(summary)
                print(f"Success: Processed {len(df)} records for year {year}.")
            else:
                print(f"Warning: No score columns found in {filename}.")

        except Exception as e:
            print(f"Fatal error processing {filename}: {e}")

    if aggregated_results:
        results_df = pd.DataFrame(aggregated_results)
        print("\nYearly Aggregated Results:")
        print(results_df.set_index('Рік'))

        plot_progression(results_df)
        print("\nAll tasks completed. Visualizations saved to 'plots/progression/'.")
    else:
        print("No results to aggregate.")
