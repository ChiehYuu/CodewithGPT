import pandas as pd

from src.kpis import basic_kpis, retention


def test_basic_kpis_and_retention():
    df = pd.DataFrame({
        "user": [1, 1, 2, 3],
        "order": ["o1", "o2", "o3", "o4"],
        "revenue": [100, 150, 200, 120],
        "date": pd.date_range("2023-01-01", periods=4, freq="M"),
    })
    metrics = basic_kpis(df, user_id="user", order_id="order", revenue="revenue")
    assert metrics["客單價"] == metrics["營收"] / metrics["交易數"]
    ret = retention(df, "user", "date", "M")
    assert "cohort" in ret.columns
