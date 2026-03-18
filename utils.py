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


SCHOOL_COL = 'Заклад освіти учасника'
GENDER_COL = 'Стать'
TERRITORY_COL = 'Тип території'

HUM_SUBJECTS = ['Українська мова', 'Українська література', 'Історія України', 'Англійська мова', 'Французька мова', 'Німецька мова', 'Іспанська мова']
TECH_SUBJECTS = ['Математика', 'Фізика', 'Хімія', 'Біологія', 'Географія']

LOWER_MAPPING = {
    **{k.lower(): v for k, v in MAPPING.items()},
    **{k.lower(): v for k, v in SUBJECT_NORMALIZATION.items()},
}


def read_prepared(csv_path: str) -> DataFrame:
    df = pd.read_csv(csv_path, sep=';', decimal=',', na_values=['null'], low_memory=False)
    score_cols = [col for col in df.columns if 'Ball100' in col]
    return df.dropna(subset=score_cols, how='all')


def clean_and_rename(df):
    return df.rename(columns=lambda col: LOWER_MAPPING.get(col.lower(), col))


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def get_score_columns(df: pd.DataFrame):
    subjects = set(SUBJECT_NORMALIZATION.values())
    return [c for c in df.columns if c in subjects]


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




def extract_year(path: str) -> int:
    match = re.search(r"\d{4}", os.path.basename(path))
    return int(match.group()) if match else 0


def run_yearly_analysis(df, func, title):
    print(f"\n===== {title} (Yearly) =====")
    for year, group in sorted(df.groupby("Year")):
        print(f"\n--- {year} ---")
        func(group)


def add_mean_score(df):
    df = df.copy()
    score_cols = get_score_columns(df)
    df["mean_score"] = df[score_cols].mean(axis=1)
    return df


def add_group_score(df, subjects=None):
    if subjects is None:
        score_cols = get_score_columns(df)
    else:
        score_cols = [c for c in subjects if c in df.columns]

    if not score_cols:
        return None

    df = df.copy()
    has_score = df[score_cols].notna().any(axis=1)
    df = df[has_score]
    df["group_score"] = df[score_cols].mean(axis=1)
    return df


def get_gender_metrics(df):
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
            "bias": male_ratio / female_ratio if female_ratio else np.nan
        })

    return pd.DataFrame(rows)