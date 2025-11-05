import pandas as pd

from src.econometrics import diff_in_diff


def test_diff_in_diff():
    df = pd.DataFrame({
        "y": [10, 12, 14, 16],
        "treat": [0, 0, 1, 1],
        "post": [0, 1, 0, 1],
        "interaction": [0, 0, 0, 1],
    })
    result = diff_in_diff(df, "y ~ treat + post + interaction")
    assert "interaction" in result.params
