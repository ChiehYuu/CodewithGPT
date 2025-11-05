import pandas as pd

from src.cleaning import fill_missing_numeric, fill_missing_categorical, remove_duplicates


def test_cleaning_operations():
    df = pd.DataFrame({"num": [1.0, None, 3.0], "cat": ["a", None, "b"]})
    log_num = fill_missing_numeric(df, ["num"])
    assert df["num"].isna().sum() == 0
    log_cat = fill_missing_categorical(df, ["cat"])
    assert "未知" in df["cat"].values
    df = pd.concat([df, pd.DataFrame({"num": [1.0], "cat": ["a"]})], ignore_index=True)
    log_dup = remove_duplicates(df)
    assert df.shape[0] == 3
