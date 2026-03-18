import os
import re

import numpy as np
from matplotlib import pyplot as plt
from pandas import DataFrame
import pandas as pd
from sklearn.linear_model import LinearRegression

data_path = 'data'

MAPPING = {
    'outid': 'ID',
    'birth': 'Рік народження',
    'sextypename': 'Стать',
    'regname': 'Регіон реєстрації/проживання учасника',
    'areaname': 'Район/Місто реєстрації/проживання учасника',
    'tername': 'Населений пункт реєстрації/проживання учасника',
    'regtypename': 'Статус учасника',
    'tertypename': 'Тип території',
    'eoname': 'Заклад освіти учасника',
    'eotypename': 'Тип закладу освіти',
    'eoregname': 'Регіон, де розташований заклад освіти',
    'eoareaname': 'Район/Місто, де розташований заклад освіти',
    'eotername': 'Населений пункт, де розташований заклад освіти',
    'eoparent': 'Орган, якому підпорядковується заклад освіти',
    'test': 'Назва тесту',
    'testdate': 'Дата проведення тесту',
    'teststatus': 'Результат складання тесту',
    'ptregname': 'Регіон екзаменаційного центру',
    'ptareaname': 'Район екзаменаційного центру',
    'pttername': 'Населений пункт екзаменаційного центру'
}

SUBJECT_NORMALIZATION = {
    'block1ball100': 'Українська мова',
    'ukrblockball100': 'Українська мова',
    'block2ball100': 'Історія України',
    'histblockball100': 'Історія України',
    'block3ball100': 'Математика',
    'mathblockball100': 'Математика',
    'physblockball100': 'Фізика',
    'chemblockball100': 'Хімія',
    'bioblockball100': 'Біологія',
    'geoblockball100': 'Географія',
    'engblockball100': 'Англійська мова',
    'frablockball100': 'Французька мова',
    'deublockball100': 'Німецька мова',
    'spablockball100': 'Іспанська мова',
    'ukrlitblockball100': 'Українська література'
}

AGGREGATION = [f"{data_path}/Odata2022File.csv", f"{data_path}/Odata2023File.csv", f"{data_path}/Odata2024File.csv", f"{data_path}/Odata2025File.csv"]


LOWER_MAPPING = {
    **{k.lower(): v for k, v in MAPPING.items()},
    **{k.lower(): v for k, v in SUBJECT_NORMALIZATION.items()},
}


def read_prepared(csv_path: str) -> DataFrame:
    df = pd.read_csv(csv_path, sep=';', decimal=',', na_values=['null'], low_memory=False)
    # Important: Only drop if ALL major subject scores are missing, not ANY.
    # Otherwise 2023-2025 data becomes empty because no one takes all optional subjects.
    score_cols = [col for col in df.columns if 'Ball100' in col]
    return df.dropna(subset=score_cols, how='all')


def clean_and_rename(df):
    return df.rename(columns=lambda col: LOWER_MAPPING.get(col.lower(), col))


def setup_dirs():
    """Create directory structure for organized plots."""
    dirs = [
        'plots/distributions',
        'plots/gender',
        'plots/correlations',
        'plots/progression'
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def get_score_columns(df: pd.DataFrame):
    subjects = set(SUBJECT_NORMALIZATION.values())
    return [c for c in df.columns if c in subjects]


def sanitize_filename(name: str):
    return name.replace(" ", "_").replace("(", "").replace(")", "")


def prepare_years(df, forecast_years):
    years = np.array(sorted(df["Year"].unique()))
    future = np.arange(years[-1] + 1, years[-1] + forecast_years + 1)
    all_years = np.concatenate([years, future])
    return years, future, all_years.reshape(-1, 1)


def fit_and_predict(x, y, x_all):
    model = LinearRegression().fit(x, y)
    return model, model.predict(x_all)


def save_plot(path, title, xlabel, ylabel, xticks=None, grid_alpha=0.3):
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if xticks is not None:
        plt.xticks(xticks)

    plt.grid(alpha=grid_alpha)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def get_score_columns(df):
    subjects = set(SUBJECT_NORMALIZATION.values())
    return [c for c in df.columns if c in subjects]


def extract_year(path: str) -> int:
    match = re.search(r"\d{4}", os.path.basename(path))
    return int(match.group()) if match else 0