from pandas import DataFrame
import pandas as pd

# Column mapping based on provided image (with handling for different variants)
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

# Cross-year normalization for subject scores (Ball100 scale)
SUBJECT_NORMALIZATION = {
    'block1ball100': 'Оцінка 100-200 (Українська мова)',
    'ukrblockball100': 'Оцінка 100-200 (Українська мова)',
    'block2ball100': 'Оцінка 100-200 (Історія України)',
    'histblockball100': 'Оцінка 100-200 (Історія України)',
    'block3ball100': 'Оцінка 100-200 (Математика)',
    'mathblockball100': 'Оцінка 100-200 (Математика)'
}

LOWER_MAPPING = {
    **{k.lower(): v for k, v in MAPPING.items()},
    **{k.lower(): v for k, v in SUBJECT_NORMALIZATION.items()},
}


def read_prepared(csv_path: str) -> DataFrame:
    return pd.read_csv(csv_path, sep=';', decimal=',', na_values=['null'], low_memory=False)


def clean_and_rename(df):
    return df.rename(columns=lambda col: LOWER_MAPPING.get(col.lower(), col))
