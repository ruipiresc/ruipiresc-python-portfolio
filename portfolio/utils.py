from typing import Any
import pandas as pd

def to_dict(obj) -> dict:
    result: dict = {}
    for column, value in obj.__dict__.items():
        if column.startswith('_'): continue
        result[column] = value
    return result

def to_format(obj) -> dict:
    result: dict = {}
    for column, value in obj.__dict__.items():
        if column.startswith('_'): continue
        result[column] = type(value)
    return result

def to_df(obj: Any) -> pd.DataFrame:
    if not isinstance(obj, list):
        return pd.DataFrame([obj.to_dict()])
    return pd.DataFrame([o.to_dict() for o in obj])