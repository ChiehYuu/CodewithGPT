import pandas as pd

from src.elasticity import estimate_price_elasticity


def test_estimate_price_elasticity():
    df = pd.DataFrame({
        "quantity": [10, 12, 9, 11],
        "price": [100, 95, 105, 98],
    })
    result = estimate_price_elasticity(df, "quantity", "price")
    assert isinstance(result.elasticity, float)
